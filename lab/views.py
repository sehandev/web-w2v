from django.shortcuts import render

from .scripts.w2v import searchpert_w2v

def w2v_1(request):
    render_dict = {
        'sample_words' : ['조례', '안전', '대통령', '인공지능', '보안', '블록체인'],
        'keyword' : '',
        'error_message' : ['' for _ in range(searchpert_w2v.term_count)],
        'result_list' : ['' for _ in range(searchpert_w2v.term_count)],
        'word_count_list' : ['' for _ in range(searchpert_w2v.term_count)]
    }

    if request.method == 'POST':
        render_dict['keyword'] = request.POST.get('search_word')
                
        for i in range(searchpert_w2v.term_count):
            similar_list, similar_word_count, word_count = searchpert_w2v.most_similar(keyword, searchpert_w2v.term_name[i], 100)

            if similar_list == -1:
                render_dict['error_message'][i] = '찾는 결과가 없습니다.'
            else:
                render_dict['word_count_list'][i] = '단어 빈도수 : ' + str(word_count) + '개'
                render_dict['result_list'][i] = []
                for j in range(len(similar_list)):
                    render_dict['result_list'][i].append(similar_list[j][0] + ' : ' + str(round(similar_list[j][1] * 100, 4)) + ' (' + str(similar_word_count[j]) + '개)')

    return render(request, 'lab/w2v_1.html', {'keyword' : keyword, 'render_dict' : render_dict})


def w2v_2(request):
    render_dict = {
        'sample_words' : ['조례', '안전', '대통령', '인공지능', '보안', '블록체인'],
        'keyword' : '',
        'error_message' : ['' for _ in range(searchpert_w2v.term_count)],
        'result_list' : ['' for _ in range(searchpert_w2v.term_count)],
        'word_count_list' : ['' for _ in range(searchpert_w2v.term_count)]
    }

    if request.method == 'POST':
        render_dict['keyword'] = request.POST.get('search_word')
                
        for i in range(searchpert_w2v.term_count):
            similar_list, similar_word_count, word_count = searchpert_w2v.most_similar(keyword, searchpert_w2v.term_name[i], 100)

            if similar_list == -1:
                render_dict['error_message'][i] = '찾는 결과가 없습니다.'
            else:
                render_dict['word_count_list'][i] = '단어 빈도수 : ' + str(word_count) + '개'
                render_dict['result_list'][i] = []
                for j in range(len(similar_list)):
                    render_dict['result_list'][i].append(similar_list[j][0] + ' : ' + str(round(similar_list[j][1] * 100, 4)) + ' (' + str(similar_word_count[j]) + '개)')

    return render(request, 'lab/w2v_2.html', {'keyword' : keyword, 'render_dict' : render_dict})
