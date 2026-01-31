def answer(request):
    global current_question_index
    global is_prescription_query
    global user_answers
    global current_question_index1
    # 一系列问题列表
    first_series_questions = [
        "请问您有什么不适的症状？",
        "还有什么症状？",
        "还有呢?"



        # 可以继续添加更多问题
    ]

    # 第二系列问题列表
    second_series_questions = [
        "您感到有没有头痛的情况？",
        "是否有喉咙痛或者咳嗽的症状？",
        "您是否有发热的感觉？",
        # 可以继续添加更多问题
    ]

    if request.method == "POST":
        question = request.POST.get('msg')
        try:
            answer = ''
            print(question)
            print(user_answers)
            if question:
                if "2" in question:  # 查药方
                    answer = "请输入药方："
                    is_prescription_query = True
                elif "1" in question:  # 问诊
                    is_prescription_query = False


                    if "感冒" in user_answers:  # 检查用户是否输入了感冒

                        if current_question_index1 < len(second_series_questions):  # 提问第二系列问题
                            answer = second_series_questions[current_question_index1]
                            current_question_index1 += 1
                        else:
                            # 匹配药方
                            matched_prescription = KBQA1.filter_prescription_by_indications(user_answers)
                            if matched_prescription:
                                prescription_info = f"{'药方'}: {matched_prescription['药方']}<br>{'主治'}: {matched_prescription['主治']}<br>{'方剂类型'}: {matched_prescription['方剂类型']}<br>{'用法'}: {matched_prescription['用法']}<br>{'组成'}: {matched_prescription['组成']}"
                                answer = f"根据您的回答，建议您尝试药方：<br>{prescription_info}"
                            else:
                                answer = "很抱歉，没有找到匹配的药方。"


                    else:
                        # 提问第一系列问题
                        if current_question_index < len(first_series_questions):
                            answer = first_series_questions[current_question_index]
                            current_question_index += 1
                        else:
                            # 记录用户的所有回答并匹配药方
                            user_answers.append(question)
                            matched_prescription = KBQA1.filter_prescription_by_indications(user_answers)
                            if matched_prescription:
                                prescription_info = f"{'药方'}: {matched_prescription['药方']}<br>{'匹配度'}: {matched_prescription['匹配度']}<br>{'主治'}: {matched_prescription['主治']}<br>{'方剂类型'}: {matched_prescription['方剂类型']}<br>{'用法'}: {matched_prescription['用法']}<br>{'组成'}: {matched_prescription['组成']}"
                                answer = f"根据您的回答，建议您尝试药方：<br>{prescription_info}"
                            else:
                                answer = "很抱歉，没有找到匹配的药方。"
                elif is_prescription_query:  # 查药方
                    answer = KBQA1.match_cure_for_condition(question)
                    # 在输出药方的结果后，添加新的提示
                    if not answer:
                        prescription_info = KBQA1.match_cure_for_condition1(question)
                        if prescription_info:
                            answer = f"根据您的回答，建议您尝试药方：<br>{prescription_info}"
                        else:
                            answer = "很抱歉，没有找到匹配的药方。"
                    is_prescription_query = True
                else:  # 问诊
                    user_answers.append(question)
                    print(user_answers)
                    if "感冒" in user_answers:  # 检查用户是否输入了感冒

                        if current_question_index1 < len(second_series_questions):  # 提问第二系列问题
                            answer = second_series_questions[current_question_index1]
                            current_question_index1 += 1
                        else:
                            # 匹配药方
                            matched_prescription = KBQA1.filter_prescription_by_indications(user_answers)
                            if matched_prescription:
                                prescription_info = f"{'药方'}: {matched_prescription['药方']}<br>{'匹配度'}: {matched_prescription['匹配度']}<br>{'主治'}: {matched_prescription['主治']}<br>{'方剂类型'}: {matched_prescription['方剂类型']}<br>{'用法'}: {matched_prescription['用法']}<br>{'组成'}: {matched_prescription['组成']}"
                                answer = f"根据您的回答，建议您尝试药方：<br>{prescription_info}"
                            else:
                                answer = "很抱歉，没有找到匹配的药方1。"
                    else:
                        # 继续提问第一系列问题
                        if current_question_index < len(first_series_questions):
                            answer = first_series_questions[current_question_index]
                            current_question_index += 1
                        else:
                            # 记录用户的所有回答并匹配药方
                            matched_prescription = KBQA1.filter_prescription_by_indications(user_answers)
                            if matched_prescription:
                                prescription_info = f"{'药方'}: {matched_prescription['药方']}<br>{'主治'}: {matched_prescription['主治']}<br>{'方剂类型'}: {matched_prescription['方剂类型']}<br>{'用法'}: {matched_prescription['用法']}<br>{'组成'}: {matched_prescription['组成']}"
                                answer = f"根据您的回答，建议您尝试药方：<br>{prescription_info}"
                            else:
                                answer = "很抱歉，没有找到匹配的药方2。"
        except Exception as e:
            print(e)
            answer = "对不起，您的问题我不知道，我今后会努力改进的。"
        return JsonResponse({'answer': answer})
    return render(request, "answer.html", {'active_menu': 'answer'})