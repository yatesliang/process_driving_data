from scipy import stats
import scipy.signal as signal
import numpy as np
from calculate_ttc import preprocess
num = [439.439819,419.119904,386.099884,406.419739,414.039978,375.940002,363.239929,355.619965,358.159882,365.779755]
print((signal.medfilt(num, kernel_size=3)))
print(np.std(num))

# testList = []
# for i in range(0,201):
#     temp = {}
#     temp['laneOffset'] = i%10
#     testList.append(temp)
# print(preprocess(testList))