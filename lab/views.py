from django.shortcuts import render

from .scripts.w2v import searchpert_w2v

# Create your views here.

def index(request):
    return render(request, 'lab/index.html', {'index_active' : 'colorlib-active'})

def member(request):
    return render(request, 'lab/member.html', {
        'member_active' : 'colorlib-active',
        'member_name' : 'sungdon_kim',
        "numbers": range(3)})

def member_single(request):
    return render(request, 'lab/member_single.html', {
        'member_active' : 'colorlib-active',
        'member_name' : 'sungdon_kim'})

def blog(request):
    return render(request, 'lab/blog.html', {'blog_active' : 'colorlib-active'})

def contact(request):
    return render(request, 'lab/contact.html', {'contact_active' : 'colorlib-active'})

def remove_duplicate(keyword):
    similar_list = []
    word_list = []
    count_list = []
    similar_counts = []
    for i in range(2):
        tmp, similar_word_count, word_count = searchpert_w2v.most_similar(keyword, i, 100 * 3)
        if tmp == -1:
            return -1, ['', '']
        else:
            count_list.append("단어 빈도수 : " + str(word_count) + "개")
            similar_list.append(tmp)
            tmp, _ = zip(*similar_list[i])
            word_list.append(set(tmp))
            similar_counts.append(similar_word_count)

    new_list = []
    new_list.append(list(word_list[0] - word_list[1]))
    new_list.append(list(word_list[1] - word_list[0]))

    return_list = [[], []]
    for i in range(2):
        for j in range(len(similar_list[i])):
            if similar_list[i][j][0] in new_list[i][:100]:
                return_list[i].append(similar_list[i][j][0] + " : " + str(round(similar_list[i][j][1] * 100, 4)) + " (" + str(similar_counts[i][j]) + "개)")

    return return_list, count_list

def searchpert_origin(request):
    term = 'Origin : 2013.03.01 ~ 2015.08.31 / 2017.05.01 ~ 2019.10.31'
    sample_words = ['조례', '안전', '대통령', '인공지능', '보안']
    keyword = ''
    result_list = ['', '']
    error_message = ['', '']
    word_count_list = ['', '']

    if request.method == 'POST':
        keyword = request.POST.get('search_word')
        duplicate_radio = request.POST.get('duplicate')

        if duplicate_radio == 'remove':
            want_remove = True
        elif duplicate_radio == 'remain':
            want_remove = False
        else:
            want_remove = -1


        if want_remove:
            result_list, word_count_list = remove_duplicate(keyword)
            if result_list == -1:
                # 2개 중 하나에 keyword가 없으면 중복 제거의 의미가 없음
                want_remove = False

        if not want_remove:
            for i in range(2):
                similar_list, word_count = searchpert_w2v.most_similar(keyword, i, 100, 'origin')

                if similar_list == -1:
                    error_message[i] = '찾는 결과가 없습니다.'
                else:
                    word_count_list[i] = "단어 빈도수 : " + str(word_count) + "개"
                    result_list[i] = []
                    for tmp_set in similar_list:
                        result_list[i].append(tmp_set[0] + " : " + str(round(tmp_set[1] * 100, 4)) + "%")

    return render(request, 'lab/searchpert.html', {'searchpert_origin_active' : 'colorlib-active', 'term' : term, 'sample_words' : sample_words, 'keyword' : keyword, 'version_url' : '/searchpert_origin',
                                                'result_list_0' : result_list[0], 'result_list_1' : result_list[1],
                                                'error_message_0' : error_message[0], 'error_message_1' : error_message[1],
                                                'word_count_0' : word_count_list[0], 'word_count_1' : word_count_list[1]
                                                })

def searchpert_reverse(request):
    term = 'Reverse : 2013.03.01 ~ 2015.08.31 / 2017.05.01 ~ 2019.10.31'
    sample_words = ['조례', '안전', '대통령', '인공지능', '보안']
    keyword = ''
    result_list = ['', '']
    error_message = ['', '']
    word_count_list = ['', '']

    if request.method == 'POST':
        keyword = request.POST.get('search_word')
        duplicate_radio = request.POST.get('duplicate')

        if duplicate_radio == 'remove':
            want_remove = True
        elif duplicate_radio == 'remain':
            want_remove = False
        else:
            want_remove = -1


        if want_remove:
            result_list, word_count_list = remove_duplicate(keyword)
            if result_list == -1:
                # 2개 중 하나에 keyword가 없으면 중복 제거의 의미가 없음
                want_remove = False

        if not want_remove:
            for i in range(2):
                similar_list, word_count = searchpert_w2v.most_similar(keyword, i, 100, 'reverse')

                if similar_list == -1:
                    error_message[i] = '찾는 결과가 없습니다.'
                else:
                    word_count_list[i] = "단어 빈도수 : " + str(word_count) + "개"
                    result_list[i] = []
                    for tmp_set in similar_list:
                        result_list[i].append(tmp_set[0] + " : " + str(round(tmp_set[1] * 100, 4)) + "%")

    return render(request, 'lab/searchpert.html', {'searchpert_reverse_active' : 'colorlib-active', 'term' : term, 'sample_words' : sample_words, 'keyword' : keyword, 'version_url' : '/searchpert_reverse',
                                                'result_list_0' : result_list[0], 'result_list_1' : result_list[1],
                                                'error_message_0' : error_message[0], 'error_message_1' : error_message[1],
                                                'word_count_0' : word_count_list[0], 'word_count_1' : word_count_list[1]
                                                })

def searchpert_shuffle(request):
    term = '2013.03.01 ~ 2015.08.31 / 2017.05.01 ~ 2019.10.31'
    sample_words = ['조례', '안전', '대통령', '인공지능', '보안']
    keyword = ''
    result_list = ['', '']
    error_message = ['', '']
    word_count_list = ['', '']

    if request.method == 'POST':
        keyword = request.POST.get('search_word')
        duplicate_radio = request.POST.get('duplicate')

        if duplicate_radio == 'remove':
            want_remove = True
        elif duplicate_radio == 'remain':
            want_remove = False
        else:
            want_remove = -1


        if want_remove:
            result_list, similar_word_count, word_count_list = remove_duplicate(keyword)
            if result_list == -1:
                # 2개 중 하나에 keyword가 없으면 중복 제거의 의미가 없음
                want_remove = False
                result_list = [[], []]

        if not want_remove:
            for i in range(2):
                similar_list, similar_word_count, word_count = searchpert_w2v.most_similar(keyword, i, 100, 'shuffle')

                if similar_list == -1:
                    error_message[i] = '찾는 결과가 없습니다.'
                else:
                    word_count_list[i] = "단어 빈도수 : " + str(word_count) + "개"
                    result_list[i] = []
                    for j in range(len(similar_list)):
                        result_list[i].append(similar_list[j][0] + " : " + str(round(similar_list[j][1] * 100, 4)) + " (" + str(similar_word_count[j]) + "개)")

    return render(request, 'lab/searchpert.html', {'searchpert_shuffle_active' : 'colorlib-active', 'term' : term, 'sample_words' : sample_words, 'keyword' : keyword, 'version_url' : '/searchpert_shuffle',
                                                'result_list_0' : result_list[0], 'result_list_1' : result_list[1],
                                                'error_message_0' : error_message[0], 'error_message_1' : error_message[1],
                                                'word_count_0' : word_count_list[0], 'word_count_1' : word_count_list[1]
                                                })
