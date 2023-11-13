def parse_answer_key(answer_key):
    result_dict = {}
    for i, val in enumerate(answer_key):
        if isinstance(val, int):
            result_dict[i] = val - 1
        elif isinstance(val, str) and val.lower() in ('a', 'b', 'c', 'd'):
            result_dict[i] = ord(val.lower()) - ord('a')
    return result_dict

# Example usage with your provided answers list:
answers = [1, 2, 1, 2, 4, 3]
result = parse_answer_key(answers)
print(result)
