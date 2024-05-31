import scipy.stats as stats
import math
def calculate_average():
  with open('measurements.txt', 'r') as file:
    lines = file.readlines()
    total_time = 0
    x1_prime = []

    total_time_per_box = 0    
    x1 = []
    
    N1 = 0
    sigma1 = None

    time_to_reach_object = 0
    x2 = []
    N2 = 0

    boxes = None

    for line in lines:
      if 'BOXES:' in line:
        boxes = int(line.split(' ')[1].strip('\n'))
        
      elif 'total_time' in line:
        total_time_per_box += float(line.split(' ')[1].strip('\n'))/boxes
        total_time += float(line.split(' ')[1].strip('\n'))
        x1.append(float(line.split(' ')[1].strip('\n'))/boxes)
        x1_prime.append(float(line.split(' ')[1].strip('\n')))
        N1+=1
      elif 'time_to_reach_object' in line:
        time_to_reach_object += float(line.split(' ')[1].strip('\n'))
        x2.append(float(line.split(' ')[1].strip('\n')))
        N2+=1
    
    sum_ = 0
    meu = total_time_per_box/N1
    for i in x1:
      sum_ = (sum_ + (i - meu)**2)
    
    sigma1 = math.sqrt(sum_/N1)


    sum_ = 0
    meu = total_time/N1
    for i in x1_prime:
      sum_ = (sum_ + (i - meu)**2)
    
    sigma1_prime = math.sqrt(sum_/N1)

    sum_ = 0
    meu = time_to_reach_object/N2
    for i in x2:
      sum_ = (sum_ + (i - meu)**2)
    
    sigma2 = math.sqrt(sum_/N1)
    
    return (total_time_per_box/N1, total_time/N1, time_to_reach_object/N2), (sigma1, sigma1_prime, sigma2), N1, N2

(total_time_per_box_mean, total_time_mean, time_to_reach_mean), (total_time_per_box_std, total_time_std, time_to_reach_std), N1, N2 =  calculate_average()
# print(total_time_per_box_mean, time_to_reach_mean, total_time_per_box_std, time_to_reach_std )
print(total_time_std, total_time_mean)

# Sample size
n1 = N1
n2 = 30

# Mean time
mean1 = total_time_mean
mean2 = 185.90

# Standard deviation
std1 = total_time_std
std2 = 31.91

# Calculate the t statistic and two-tailed p value
t_stat, p_value = stats.ttest_ind_from_stats(mean1, std1, n1, mean2, std2, n2)

print(f"t statistic: {t_stat}")
print(f"p value: {p_value}")



# Python
import pandas as pd

data = []
with open('measurements.txt', 'r') as file:
    box_data = {}
    for line in file:
        if line.strip() == '':
            continue
        key, value = line.strip().split(': ')
        if key == 'BOXES':
            if box_data:
                data.append(box_data)
            box_data = {'BOXES': int(value), 'time_to_look_for_object': [], 'time_to_reach_object': []}
        elif key in ['time_to_look_for_object', 'time_to_reach_object']:
            box_data[key].append(float(value))
        elif key == 'total_time':
            box_data['total_time'] = float(value)
    if box_data:
        data.append(box_data)

df = pd.DataFrame(data)
df['time_to_look_for_object'] = df['time_to_look_for_object'].apply(lambda x: ', '.join(map(str, x)))
df['time_to_reach_object'] = df['time_to_reach_object'].apply(lambda x: ', '.join(map(str, x)))

# Add experiment_number column
df.insert(0, 'experiment_number', range(1, 1 + len(df)))

markdown_table = df.to_markdown(index=False)
# print(markdown_table)