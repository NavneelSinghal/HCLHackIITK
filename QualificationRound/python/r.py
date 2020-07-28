import urllib3
def main():
    input1='https://mettl-arq.s3-ap-southeast-1.amazonaws.com/questions/iit-kanpur/cyber-security-hackathon/round1/problem1/defaulttestcase.txt'
    try:
        r = urllib3.PoolManager().request('GET', input1)
    except:
        return ({0:0}, 'the URL is incorrect') 

    # alternative 1:
    if r.headers['Content-Type'][:4] != 'text':
        return ({0:0}, 'file is not a text file')

    # alternative 2:
    if input1[-4:] != '.txt':
        return ({0:0}, 'file is not a text file')

    l = r.data.decode('utf-8').split('\n')
    d = {}
    for i in range(len(l)):
        s = ''.join(l[i].split(' '))
        s = s.lower()
        if s == s[-1::-1] && len(s) != 0:
            d[i+1] = len(s)
    if len(d) == 0:
        d = {0:0}
    return (d, 'file ok')

print(main())
