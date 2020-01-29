from django.shortcuts import render

from .scripts.w2v import searchpert_w2v

def w2v_1(request):
    keyword = ''
    render_dict = {
        'sample_words' : ['조례', '안전', '대통령', '인공지능', '보안', '블록체인'],
        'error_message' : ['' for _ in range(searchpert_w2v.term_count)],
        'result_list' : ['' for _ in range(searchpert_w2v.term_count)],
        'word_count_list' : ['' for _ in range(searchpert_w2v.term_count)]
    }

    if request.method == 'POST':
        keyword = request.POST.get('search_word')
                
        for i in range(searchpert_w2v.term_count):
            similar_list, similar_word_count, word_count = searchpert_w2v.most_similar(keyword, searchpert_w2v.term_name[i], 100)

            if similar_list == -1:
                render_dict['error_message'][i] = '찾는 결과가 없습니다.'
            else:
                render_dict['word_count_list'][i] = f'단어 빈도수 : {word_count}개, {round(word_count / searchpert_w2v.term_counts[i], 3)}%'
                render_dict['result_list'][i] = []
                for j in range(len(similar_list)):
                    cosine_similarity = round(similar_list[j][1] * 100, 2)
                    count_ratio = round(similar_word_count[j] / searchpert_w2v.term_counts[i], 3)
                    render_dict['result_list'][i].append(f'{similar_list[j][0]} : {cosine_similarity} ({similar_word_count[j]}개, {count_ratio}%)')

    return render(request, 'lab/w2v_1.html', {'keyword' : keyword, 'render_dict' : render_dict})


def w2v_2(request):
    keyword = ''
    render_dict = {
        'sample_words' : ['조례', '안전', '대통령', '인공지능', '보안', '블록체인'],
        'error_message' : ['' for _ in range(searchpert_w2v.term_count)],
        'result_list' : ['' for _ in range(searchpert_w2v.term_count)],
        'word_count_list' : ['' for _ in range(searchpert_w2v.term_count)]
    }

    if request.method == 'POST':
        keyword = request.POST.get('search_word')
                
        for i in range(searchpert_w2v.term_count):
            similar_list, similar_word_count, word_count = searchpert_w2v.most_similar(keyword, searchpert_w2v.term_name[i], 100)

            if similar_list == -1:
                render_dict['error_message'][i] = '찾는 결과가 없습니다.'
            else:
                render_dict['word_count_list'][i] = f'단어 빈도수 : {word_count}개, {round(word_count / searchpert_w2v.term_counts[i], 3)}%'
                render_dict['result_list'][i] = []
                for j in range(len(similar_list)):
                    cosine_similarity = round(similar_list[j][1] * 100, 2)
                    count_ratio = round(similar_word_count[j] / searchpert_w2v.term_counts[i], 3)
                    render_dict['result_list'][i].append(f'{similar_list[j][0]} : {cosine_similarity} ({similar_word_count[j]}개, {count_ratio}%)')

    return render(request, 'lab/w2v_2.html', {'keyword' : keyword, 'render_dict' : render_dict})
