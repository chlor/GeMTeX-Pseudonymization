import spacy
    

class SpacyNlp:
    """
    spacy tokenizer and parser
    """

    def __init__(self):
        self.nlp = spacy.load('de_core_news_sm', disable=['ner'])
    
    # process text with spacy
    def get_spacy_doc(self, sg_file):
        sg_file.doc = self.nlp(sg_file.txt)
        sg_file.det = sg_file.doc.vocab.strings.add('DET')
        sg_file.artWords = set([sg_file.doc.vocab.strings.add('ADJ'), sg_file.det])
        sg_file.apprart = sg_file.doc.vocab.strings.add('APPRART')
        sg_file.genitive = set([sg_file.doc.vocab.strings.add(label) for label in ('ag','og')])
        sg_file.dative = sg_file.doc.vocab.strings.add('da')

    def get_spacy_token(self, sg_file, start, end):
        """get spacy token by indices and merge tokens if necessary"""
        if not sg_file.doc:
            self.get_spacy_doc(sg_file)
        span = sg_file.doc.char_span(start, end)
        if span:
            if len(span) > 1:
                with sg_file.doc.retokenize() as retokenizer:
                    retokenizer.merge(span)
            return sg_file.doc[span.start]
        else:          
            for token in sg_file.doc:
                if start >= token.idx:
                    if end <= token.idx+len(token):
                        return token
                    else:
                        start_span = token.i
                        for tokenEnd in sg_file.doc[token.i + 1:]:
                            if end <= tokenEnd.idx+len(tokenEnd):
                                end_span = tokenEnd.i+1
                        with sg_file.doc.retokenize() as retokenizer:
                            span = sg_file.doc[start_span:end_span]
                            retokenizer.merge(span)
                            return sg_file.doc[span.start]
