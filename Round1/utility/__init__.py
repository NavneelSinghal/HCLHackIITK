from .dir import *

# import os

# classes = [
#         'Benign',
#         'Malware/Backdoor',
#         'Malware/Trojan',
#         'Malware/TrojanDownloader',
#         'Malware/TrojanDropper',
#         'Malware/Virus',
#         'Malware/Worm'
#         ]

# def get_files(directory):
#     '''Given directory return files (hash) in it'''
#     l = []
#     for f in os.scandir(directory):
#         l.append(f.path)
#     return l

# def get_all(root):
#     l = []
#     for cl in classes:
#         try:
#             l += get_files(os.path.join(root, cl))
#         except:
#             l += []
#     return l
# def get_malwares(root):
#     l = []
#     for cl in classes[1:]:
#         try:
#             l += get_files(os.path.join(root, cl))
#         except:
#             l += []
#     return l
# def get_benigns(root):
#     return get_files(os.path.join(root, classes[0]))
# def get_backdoors(root):
#     return get_files(os.path.join(root, 'Malware/Backdoor'))
# def get_trojans(root):
#     return get_files(os.path.join(root, 'Malware/Trojan'))
# def get_trojandownloaders(root):
#     return get_files(os.path.join(root, 'Malware/TrojanDownloader'))
# def get_trojandroppers(root):
#     return get_files(os.path.join(root, 'Malware/TrojanDropper'))
# def get_viruses(root):
#     return get_files(os.path.join(root, 'Malware/Virus'))
# def get_worms(root):
#     return get_files(os.path.join(root, 'Malware/Worm'))
