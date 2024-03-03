def get_proxy():
    '''format: str'''
    fpath = 'proxy.txt'
    with open(fpath, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    return lines[0].strip()