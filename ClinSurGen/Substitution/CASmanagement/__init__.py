import collections

from cassis import Cas, load_typesystem

from ClinSurGen.Substitution.Entities.Age import sub_age
from ClinSurGen.Substitution.Entities.Date import *
from ClinSurGen.Substitution.Entities.Name import *
from ClinSurGen.Substitution.Entities.Location import *
from ClinSurGen.Substitution.Entities.Id import *
from ClinSurGen.Substitution.KeyCreator import *
from ClinSurGen.Substitution.SubstUtils import get_pattern


from const import HOSPITAL_DATA_PATH, HOSPITAL_NEAREST_NEIGHBORS_MODEL_PATH, EMBEDDING_MODEL_NAME, SPACY_MODEL


def manipulate_cas(cas, mode, config):
    logging.info('manipulate text and cas - mode: ' + mode)
    if mode in ['X', 'entity']:
        return manipulate_cas_simple(cas, mode)
    elif mode == 'gemtex':
        return manipulate_cas_gemtex(cas, config)
    elif mode == 'fictive_names':
        return manipulate_cas_fictive(cas, config)
    else:
        exit(1)


def set_shift_and_new_text(token, replace_element, last_token_end, shift, new_text, sofa):
    new_text = new_text + sofa.sofaString[last_token_end:token.begin] + replace_element
    new_end = len(new_text)

    shift.append((token.end, len(replace_element) - len(token.get_covered_text())))
    last_token_end = token.end

    token.begin = new_end - len(replace_element)
    token.end = new_end

    return new_text, new_end, shift, last_token_end, token.begin, token.end


def manipulate_sofa_string_in_cas(cas, new_text, shift):
    shift_add = 0

    for sentence in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'):
        for sen in cas.select_covered('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence', sentence):
            if shift:
                new_begin = sen.begin + shift_add
                new_end = sen.end + shift_add
            else:
                new_begin = sen.begin + shift_add
                new_end = sen.end + shift_add

            sen.begin = new_begin
            sen.end = new_end

    cas.sofa_string = new_text

    return cas


def prepare_cas_for_semantic_annotation(cas, norm_dates):

    file_typesystem = 'resources/double-layer/TypeSystem.xml'  # todo @chlor

    with open(file_typesystem, 'rb') as f:
        new_typesystem = load_typesystem(f)

    cas_sem = Cas(
        typesystem=new_typesystem,
        sofa_string=cas.sofa_string,  # Text
        document_language=cas.document_language
    )

    for sentence in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if token.kind == 'DATE':

                Token = new_typesystem.get_type('gemtex.Concept')
                cas_sem.add(
                    Token(
                        begin=token.begin,
                        end=token.end,
                        id='http://snomed.info/id/258695005',
                        literal=str(norm_dates[token.get_covered_text()])
                    )
                )
    return cas_sem


def manipulate_cas_simple(cas, mode):
    sofa = cas.get_sofa()
    shift = []

    new_text = ''
    last_token_end = 0

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if mode == 'X':
                replace_element = ''.join(['X' for _ in token.get_covered_text()])
                new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                    token=token,
                    replace_element=replace_element,
                    last_token_end=last_token_end,
                    shift=shift,
                    new_text=new_text,
                    sofa=sofa,
                )

            elif mode == 'entity':
                replace_element = str(token.kind)
                new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                    token=token,
                    replace_element=replace_element,
                    last_token_end=last_token_end,
                    shift=shift,
                    new_text=new_text,
                    sofa=sofa,
                )
            else:
                exit(-1)

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift)


def manipulate_cas_gemtex(cas, config):
    sofa = cas.get_sofa()
    annotations = collections.defaultdict(set)
    dates = []

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if token.kind is not None:

                if token.kind not in ['PROFESSION', 'AGE']:
                    if token.kind != 'DATE':
                        annotations[token.kind].add(token.get_covered_text())

                    if token.kind == 'DATE':
                        if token.get_covered_text() not in dates:
                            dates.append(token.get_covered_text())

                    if token.kind == 'DATE_BIRTH':
                        if token.get_covered_text() not in dates:
                            dates.append(token.get_covered_text())

                    if token.kind == 'DATE_DEATH':
                        if token.get_covered_text() not in dates:
                            dates.append(token.get_covered_text())

            else:
                logging.warning('token.kind: NONE - ' + token.get_covered_text())

    random_keys = get_n_random_keys(sum([len(annotations[label_type]) for label_type in annotations]))
    key_ass = {}
    key_ass_ret = {}
    i = 0
    for label_type in annotations:
        key_ass[label_type] = {}

        if label_type not in ['DATE']:
            key_ass_ret[label_type] = {}

        for annotation in annotations[label_type]:
            if label_type not in ['DATE', 'DATE_BIRTH', 'DATE_DEATH']:
                key_ass[label_type][annotation] = random_keys[i]
                key_ass_ret[label_type][random_keys[i]] = annotation
                i = i+1

    new_text = ''
    last_token_end = 0

    if str(config['surrogate_process']['date_normalization_to_cas']) == 'true':
        norm_dates = normalize_dates(list_dates=dates)  ## input list

    shift = []

    for sentence in cas.select('webanno.custom.PHI'):

        for token in cas.select_covered('webanno.custom.PHI', sentence):

            replace_element = ''

            if token.kind is not None and token.kind not in ['PROFESSION', 'AGE']:

                if not token.kind.startswith('DATE'):
                    replace_element = '[** ' + token.kind + ' ' + key_ass[token.kind][token.get_covered_text()] + ' **]'
                else:  # DATE
                    if token.kind in ['DATE_BIRTH', 'DATE_DEATH']:

                        quarter_date = get_quarter(token.get_covered_text())
                        replace_element = '[** ' + token.kind + ' ' + quarter_date + ' **]'
                        key_ass_ret[token.kind][quarter_date] = token.get_covered_text()

                    else:
                        replace_element = token.get_covered_text()

            new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                token=token,
                replace_element=replace_element,
                last_token_end=last_token_end,
                shift=shift,
                new_text=new_text,
                sofa=sofa,
            )

    new_cas = manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift)

    if str(config['surrogate_process']['date_normalization_to_cas']) == 'true':
        cas_sem = prepare_cas_for_semantic_annotation(cas=new_cas, norm_dates=norm_dates)
        return new_cas, cas_sem, key_ass_ret

    else:
        return new_cas, key_ass_ret


def manipulate_cas_fictive(cas, config):

    sofa = cas.get_sofa()
    annotations = collections.defaultdict(set)
    # tokens = list(cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'))
    token_type = next(t for t in cas.typesystem.get_types() if 'Token' in t.name)
    tokens = cas.select(token_type.name)

    shift = []

    names = {}
    dates = {}
    hospitals = {}
    identifiers = {}
    phone_numbers = {}
    user_names = {}

    '''
    1. FOR-Schleife: ein Durchgang über Text und Aufsammeln aller Elemente in Dict-Strukturen
    '''

    for sentence in cas.select('webanno.custom.PHI'):

        for custom_phi in cas.select_covered('webanno.custom.PHI', sentence):

            if custom_phi.kind is not None:

                if custom_phi.kind in {'NAME_PATIENT', 'NAME_DOCTOR', 'NAME_RELATIVE', 'NAME_EXT', 'NAME_OTHER'}:
                    if custom_phi.get_covered_text() not in names.keys():
                        # Find tokens that precede the current PHI token
                        preceding_tokens = [token for token in tokens if token.end <= custom_phi.begin]
                        # Sort by token end offset to ensure chronological order
                        preceding_tokens.sort(key=lambda t: t.end)
                        # Get the last five preceding tokens
                        preceding_tokens = preceding_tokens[-5:] if len(preceding_tokens) >= 5 else preceding_tokens
                        # get covered text for these tokens
                        preceding_tokens = [token.get_covered_text() for token in preceding_tokens]
                        # save preceding words for each name entity
                        names[custom_phi.get_covered_text()] = preceding_tokens

                if custom_phi.kind == 'DATE':
                    if custom_phi.get_covered_text() not in dates.keys():
                        dates[custom_phi.get_covered_text()] = custom_phi.get_covered_text()

                if custom_phi.kind == 'DATE_BIRTH':
                    if custom_phi.get_covered_text() not in dates.keys():
                        dates[custom_phi.get_covered_text()] = custom_phi.get_covered_text()

                if custom_phi.kind == 'DATE_DEATH':
                    if custom_phi.get_covered_text() not in dates.keys():
                        dates[custom_phi.get_covered_text()] = custom_phi.get_covered_text()

                if custom_phi.kind == 'LOCATION_HOSPITAL':
                    if custom_phi.get_covered_text() not in hospitals.keys():
                        hospitals[custom_phi.get_covered_text()] = custom_phi.get_covered_text()

                if custom_phi.kind == 'ID':
                    if custom_phi.get_covered_text() not in identifiers.keys():
                        identifiers[custom_phi.get_covered_text()] = custom_phi.get_covered_text()

                if custom_phi.kind == 'CONTACT_PHONE' or custom_phi.kind == 'CONTACT_FAX':
                    if custom_phi.get_covered_text() not in phone_numbers.keys():
                        phone_numbers[custom_phi.get_covered_text()] = custom_phi.get_covered_text()

                if custom_phi.kind == 'NAME_USER':
                    if custom_phi.get_covered_text() not in user_names.keys():
                        user_names[custom_phi.get_covered_text()] = custom_phi.get_covered_text()

            else:
                logging.warning('custom_phi.kind: NONE - ' + custom_phi.get_covered_text())

    '''
    Nach 1. FOR-SCHLEIFE - Ersetzung der Elemente 
    '''

    # real_names --> fictive name
    # replaced_dates = surrogate_dates(dates=dates, int_delta=delta)
    replaced_dates          = dates  #surrogate_dates(dates=dates, int_delta=delta)
    replaced_names          = surrogate_names_by_fictive_names(names)
    replaced_identifiers    = surrogate_identifiers(identifiers)
    replaced_phone_numbers  = surrogate_identifiers(phone_numbers)
    replaced_user_names     = surrogate_identifiers(user_names)

    # Check if all required paths exist
    if os.path.exists(HOSPITAL_NEAREST_NEIGHBORS_MODEL_PATH) and os.path.exists(HOSPITAL_DATA_PATH):
        # Load resources
        nn_model = joblib.load(HOSPITAL_NEAREST_NEIGHBORS_MODEL_PATH)
        resource_hospital_names = load_hospital_names(HOSPITAL_DATA_PATH)
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        nlp = spacy.load(SPACY_MODEL)

    else:
        # Identify missing paths
        missing_paths = [path for path in [HOSPITAL_NEAREST_NEIGHBORS_MODEL_PATH, HOSPITAL_DATA_PATH] if not os.path.exists(path)]
        # Log a warning and raise an exception
        logging.warning(f"The following required paths do not exist: {', '.join(missing_paths)}")
        raise FileNotFoundError(f"The following required paths do not exist: {', '.join(missing_paths)}")

    replaced_hospital = {
        hospital: get_hospital_surrogate(
            target_hospital=hospital,
            model=model,
            nn_model=nn_model,
            nlp=nlp,
            hospital_names=resource_hospital_names
        )[0] for hospital in hospitals
    }

    key_ass = {}
    key_ass_ret = {}

    new_text = ''
    last_token_end = 0

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if token.kind not in key_ass_ret.keys():
                key_ass_ret[token.kind] = {}

            if token.kind is not None:

                if token.kind in {'NAME_PATIENT', 'NAME_DOCTOR', 'NAME_RELATIVE', 'NAME_EXT'}:
                    replace_element = replaced_names[token.get_covered_text()]

                elif token.kind in {'NAME_TITLE', 'NAME_USERNAME'}:
                    replace_element = token.get_covered_text()

                elif token.kind == 'DATE':
                    replace_element = token.get_covered_text()

                elif token.kind == 'DATE_BIRTH':
                    replace_element = dates[token.get_covered_text()]

                elif token.kind == 'DATE_DEATH':
                    replace_element = dates[token.get_covered_text()]

                elif token.kind == 'AGE':
                    replace_element = sub_age(token=token.get_covered_text())

                elif token.kind == 'LOCATION_HOSPITAL':
                    replace_element = replaced_hospital[token.get_covered_text()]  # todo @ marivn

                elif token.kind.startswith('LOCATION'):
                    replace_element = str(get_pattern(name_string=token.get_covered_text()))  # todo @ marivn

                elif token.kind == 'ID':
                    replace_element = replaced_identifiers[token.get_covered_text()]

                elif token.kind == 'CONTACT_PHONE' or token.kind == 'CONTACT_FAX':
                    replace_element = replaced_phone_numbers[token.get_covered_text()]

                elif token.kind == 'NAME_USER':
                    replace_element = replaced_user_names[token.get_covered_text()]

                elif token.kind.startswith('CONTACT'):
                    replace_element = str(get_pattern(name_string=token.get_covered_text()))

                elif token.kind == 'PROFESSION':
                    replace_element = token.get_covered_text()

                elif token.kind == 'OTHER':
                    logging.warning(msg='NONE ' + token.get_covered_text())
                    replace_element = token.get_covered_text()

                else:  # if token.kind is None:
                    logging.warning(msg='NONE ' + token.get_covered_text())
                    replace_element = str(len(token.get_covered_text()))

            else:  # DATE
                if token.kind in ['DATE_BIRTH', 'DATE_DEATH']:

                    quarter_date = get_quarter(token.get_covered_text())
                    replace_element = '[** ' + token.kind + ' ' + quarter_date + ' **]'
                    #key_ass_ret[token.kind][quarter_date] = token.get_covered_text()

                else:
                    replace_element = token.get_covered_text()

            #key_ass_ret[label_type][random_keys[i]] = annotation
            key_ass_ret[token.kind][replace_element] = token.get_covered_text()

            new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                token=token,
                replace_element=replace_element,
                last_token_end=last_token_end,
                shift=shift,
                new_text=new_text,
                sofa=sofa,
            )

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift), key_ass




#    new_cas = manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift)
#    if str(config['surrogate_process']['date_normalization_to_cas']) == 'true':
#        cas_sem = prepare_cas_for_semantic_annotation(cas=new_cas, norm_dates=norm_dates)
#        return new_cas, cas_sem, key_ass_ret
#
#    else:
#        return new_cas, key_ass_ret
