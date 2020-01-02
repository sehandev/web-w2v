from django.shortcuts import render

from .scripts.w2v import searchpert_w2v

def w2v_1(request):
    sample_words = ['조례', '안전', '대통령', '인공지능', '보안', '블록체인']
    keyword = ''
    error_message = ['' for _ in range(searchpert_w2v.TERM_COUNT)]
    result_list = ['' for _ in range(searchpert_w2v.TERM_COUNT)]
    word_count_list = ['' for _ in range(searchpert_w2v.TERM_COUNT)]

    if request.method == 'POST':
        keyword = request.POST.get('search_word')
                
        for i in range(searchpert_w2v.TERM_COUNT):
            similar_list, similar_word_count, word_count = searchpert_w2v.most_similar(keyword, i, 100, 'shuffle')

            if similar_list == -1:
                error_message[i] = '찾는 결과가 없습니다.'
            else:
                word_count_list[i] = '단어 빈도수 : ' + str(word_count) + '개'
                result_list[i] = []
                for j in range(len(similar_list)):
                    result_list[i].append(similar_list[j][0] + ' : ' + str(round(similar_list[j][1] * 100, 4)) + ' (' + str(similar_word_count[j]) + '개)')

    return render(request, 'lab/w2v_1.html', {'title' : '2개 정부', 'sample_words' : sample_words, 'keyword' : keyword, 'version_url' : '/w2v_1',
                                                'result_list_2' : result_list[2], 'result_list_3' : result_list[3],
                                                'error_message_2' : error_message[2], 'error_message_3' : error_message[3],
                                                'word_count_2' : word_count_list[2], 'word_count_3' : word_count_list[3]
                                                })


def w2v_2(request):
    sample_words = ['조례', '안전', '대통령', '인공지능', '보안', '블록체인']
    keyword = ''
    error_message = ['' for _ in range(searchpert_w2v.TERM_COUNT)]
    result_list = ['' for _ in range(searchpert_w2v.TERM_COUNT)]
    word_count_list = ['' for _ in range(searchpert_w2v.TERM_COUNT)]

    if request.method == 'POST':
        keyword = request.POST.get('search_word')
                
        for i in range(searchpert_w2v.TERM_COUNT):
            similar_list, similar_word_count, word_count = searchpert_w2v.most_similar(keyword, i, 100, 'shuffle')

            if similar_list == -1:
                error_message[i] = '찾는 결과가 없습니다.'
            else:
                word_count_list[i] = '단어 빈도수 : ' + str(word_count) + '개'
                result_list[i] = []
                for j in range(len(similar_list)):
                    result_list[i].append(similar_list[j][0] + ' : ' + str(round(similar_list[j][1] * 100, 4)) + ' (' + str(similar_word_count[j]) + '개)')

    return render(request, 'lab/w2v_2.html', {'title' : '4개 정부', 'sample_words' : sample_words, 'keyword' : keyword, 'version_url' : '/w2v_2',
                                                'result_list_0' : result_list[0], 'result_list_1' : result_list[1], 'result_list_2' : result_list[2], 'result_list_3' : result_list[3],
                                                'error_message_0' : error_message[0], 'error_message_1' : error_message[1], 'error_message_2' : error_message[2], 'error_message_3' : error_message[3],
                                                'word_count_0' : word_count_list[0], 'word_count_1' : word_count_list[1], 'word_count_2' : word_count_list[2], 'word_count_3' : word_count_list[3]
                                                })
