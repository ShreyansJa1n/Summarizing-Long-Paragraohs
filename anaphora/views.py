from django.shortcuts import render
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

from nltk.tag import StanfordNERTagger

# Create your views here.


def home(request):
    return render(request, 'index.html')


def summarize(request):
    text_string = request.POST['inputText']
    st = StanfordNERTagger('/Users/shreyansjain/Downloads/stanford-ner-2020-11-17/classifiers/english.all.3class.distsim.crf.ser.gz',
                           '/Users/shreyansjain/Downloads/stanford-ner-2020-11-17/stanford-ner.jar',
                           encoding='utf-8')

    def create_frequency_table(text_string) -> dict:

        stopWords = set(stopwords.words("english"))
        words = word_tokenize(text_string)
        ps = PorterStemmer()

        freqTable = dict()
        for word in words:
            word = ps.stem(word)
            if word in stopWords:
                continue
            if word in freqTable:
                freqTable[word] += 1
            else:
                freqTable[word] = 1

        return freqTable

    # text_string = '''
    # Acharya J.C. Bose was a scientist of many talents. He was born on 30 November, 1858 in Bikrampur, West Bengal. He was a polymath, physicist, biologist, botanist and archaeologist. Bose pioneered the study of radio and microwave optics. He made important contributions to the study of plants. He has laid the foundation of experimental science in the Indian sub-continent. He was the first person to use semiconductor junctions to detect radio signals. What’s more, he is also probably the father of open technology, as he made his inventions and work freely available for others to further develop and his reluctance for patenting his work is legendary.
    # Another of his well known inventions is the crescograph. He measured plant response to various stimuli and hypothesized that plants can feel pain, understand affection etc.
    # While most of us are aware of his scientific prowess, we might not be aware of his talent as an early writer of science fiction! He is in fact considered the father of Bengali science fiction.
    # '''

    # print(text_string)

    sentences = sent_tokenize(text_string)

    ogfreqTable = create_frequency_table(text_string)
    # print(ogfreqTable)

    def score_sentences(sentences, freqTable) -> dict:
        sentenceValue = dict()

        for sentence in sentences:
            word_count_in_sentence = (len(word_tokenize(sentence)))
            for wordValue in freqTable:
                if wordValue in sentence.lower():
                    if sentence[:10] in sentenceValue:
                        sentenceValue[sentence[:10]] += freqTable[wordValue]
                    else:
                        sentenceValue[sentence[:10]] = freqTable[wordValue]

            sentenceValue[sentence[:10]] = sentenceValue[sentence[:10]
                                                         ] // word_count_in_sentence

        return sentenceValue

    ogsentenceValue = score_sentences(sentences, ogfreqTable)
    # print(ogsentenceValue)

    def find_average_score(sentenceValue) -> int:
        sumValues = 0
        for entry in sentenceValue:
            sumValues += sentenceValue[entry]

        average = int(sumValues / len(sentenceValue))

        return average

    def generate_summary(sentences, sentenceValue, threshold):
        sentence_count = 0
        summary = ''

        for sentence in sentences:
            if sentence[:10] in sentenceValue and sentenceValue[sentence[:10]] > (threshold):
                summary += " " + sentence
                sentence_count += 1

        return summary

    ogthreshold = find_average_score(ogsentenceValue)
    # print(ogthreshold)
    ogsum = generate_summary(sentences, ogsentenceValue, ogthreshold)

    # print(sentences)
    tokenized_text = word_tokenize(text_string)

    classified_text = st.tag(tokenized_text)

    new_text_string = ''
    anaphora_p = ['he', 'his', 'she', 'her', 'His', 'Her', 'He', 'She']

    pointer_person = ''
    person = ''

    for i in range(0, len(tokenized_text)):
        a = tokenized_text[i]
        b = classified_text[i][1]
        if b == 'PERSON':
            pointer_person = a
       
        else:
            if a in anaphora_p:
                if len(person) == 0:
                    a = pointer_person
                else:
                    a = person
            if a == '.' or a == '!' or a == '?':
                person = pointer_person
                # print(person)
        new_text_string += a+' '

    # print(new_text_string)
    sentorg = sent_tokenize(text_string)
    sentences = sent_tokenize(new_text_string)
    freqTable = create_frequency_table(new_text_string)
    sentenceValue = score_sentences(sentences, freqTable)
    threshold = find_average_score(sentenceValue)
    # print(freqTable, sentenceValue, threshold)
    # print('\n')
    finalsum = generate_summary(sentences, sentenceValue, threshold)
    listfinal = sent_tokenize(finalsum)
    finalsent = ''
    for i in range(len(listfinal)):
        flag = 0
        for j in range(len(sentences)):
            if listfinal[i] == sentences[j]:
                finalsent += ' '+sentorg[j]
                flag = 1
                break
        if flag == 0:
            finalsent += listfinal[i]
    # print(finalsent)
    # print(ogsentenceValue)
    return render(request, 'index.html', {'anasummarized': finalsent, 'freqTable': ogfreqTable, 'sentenceScore': ogsentenceValue, 'threshold': ogthreshold, 'original': ogsum, 'input': text_string, 'anafreq': freqTable, 'anascore': sentenceValue, 'anathres': threshold})
