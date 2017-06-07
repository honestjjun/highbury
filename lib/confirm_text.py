

def confirm_text_length(string):
    string = string.strip()
    string = string.lower()
    string_encode = string.encode('cp949')
    return len(string_encode)


def no_space_text(string, input=None):
    string = string.split(' ')
    string = ''.join(string)
    if input:
        return string
    else:
        return len(string)