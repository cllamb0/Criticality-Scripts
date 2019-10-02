import os
import sys
import math
import numpy as np

def find_k():
	with open('outp','r') as filename:
		for line in filename:
			if "final result" in line:
				k_final = float(line[27:34])
	return k_final

def find_radii(problem, locator, locator2=None):
	outer_radius = None
	with open('/Users/raptor/Classes/NE-156/Homework-2/'+problem+'.txt', 'r') as filename:
		lines = filename.readlines()
		for line in lines:
			if locator in line:
				radius = float(line[5:15].strip())
		if locator2 is not None:
			for line in lines:
				if locator2 in line:
					outer_radius = float(line[6:16].strip()) - radius
	del lines
	return radius, outer_radius

def adjust_radii(problem, locator, new_text):
	with open('/Users/raptor/Classes/NE-156/Homework-2/'+problem+'.txt', 'r') as filename:
		linedata = filename.readlines()
	for i, line in enumerate(linedata):
		if locator in line:
			linedata[i] = new_text+'          $ '+locator+'\n'
	with open('/Users/raptor/Classes/NE-156/Homework-2/'+problem+'.txt', 'w') as filename:
		filename.writelines(linedata)

# Initial test run of MCNP 
prob = input('What Problem are you working on? ')

with open(prob+'.txt', 'r') as filename:
	lines = filename.readlines()
	density = float(lines[1][5:12].strip())
del lines

test_num=1
os.chdir('Outputs/Prob'+prob[0]+'/'+prob+'/')
print("Running MCNP Test #",test_num)
test_num += 1
os.system('mcnp6 i=/Users/raptor/Classes/NE-156/Homework-2/'+prob+'.txt tasks 4 >/dev/null 2>&1')
k_1 = find_k()
radius1, outer_radius1 = find_radii(prob,'Inner Sphere', 'Outer Sphere')

#Begin adjustments if necessary
print('Found k value of:',k_1)
if k_1 > 0.9995 and k_1 < 1.0005:
	print("This leaves a critical radius of:",radius1)
	m_crit = density*(4/3*math.pi*(radius1)**3)
	print('With a density of '+str(density)+', this gives us a critical mass of: '+str(round(m_crit/1000,3))+'kg')
	sys.exit()

if k_1 < 1.0:
	new_radius = radius1 + 1
	adjust_radii(prob, 'Inner Sphere', '1 so '+str(new_radius))
	if outer_radius1 is not None:
		adjust_radii(prob, 'Outer Sphere', '*2 so '+str(outer_radius1+new_radius))
else:
	new_radius = radius1 - 1
	adjust_radii(prob, 'Inner Sphere', '1 so '+str(new_radius))
	if outer_radius1 is not None:
		adjust_radii(prob, 'Outer Sphere', '*2 so '+str(outer_radius1+new_radius))
			
#Testing second run of MCNP
os.system('rm outp && rm runtpe && rm srctp')
print("Running MCNP Test #",test_num)
test_num += 1
os.system('mcnp6 i=/Users/raptor/Classes/NE-156/Homework-2/'+prob+'.txt tasks 4 >/dev/null 2>&1')
k_2 = find_k()
new_radius, io_rad = find_radii(prob, 'Inner Sphere', 'Outer Sphere')
print('Found k value of:',k_2)
if k_2 > 0.9995 and k_2 < 1.0005:
	print("This leaves a critical radius of:",radius2)
	m_crit = density*(4/3*math.pi*(radius2)**3)
	print('With a density of '+str(density)+', this gives us a critical mass of: '+str(round(m_crit/1000,3))+'kg')
	sys.exit()

sub_critical = False
if k_2 < 1:
	sub_critical = True
while sub_critical:
	new_radius = new_radius + 1
	adjust_radii(prob, 'Inner Sphere', '1 so '+str(new_radius))
	if outer_radius1 is not None:
		adjust_radii(prob, 'Outer Sphere', '*2 so '+str(outer_radius1+new_radius))
	os.system('rm outp && rm runtpe && rm srctp')
	print("Running MCNP Test #",test_num)
	test_num += 1
	os.system('mcnp6 i=/Users/raptor/Classes/NE-156/Homework-2/'+prob+'.txt tasks 4 >/dev/null 2>&1')
	k_2 = find_k()
	new_radius, io_rad = find_radii(prob, 'Inner Sphere', 'Outer Sphere')
	print('Found k value of:',k_2)
	if k_2 > 0.9995 and k_2 < 1.0005:
		print("This leaves a critical radius of:",radius2)
		m_crit = density*(4/3*math.pi*(radius2)**3)
		print('With a density of '+str(density)+', this gives us a critical mass of: '+str(round(m_crit/1000,3))+'kg')
		sys.exit()
	if k_2 > 1:
		sub_critical = False
if k_2 > k_1:
	k_values = [k_1, k_2]
	r_values = [radius1, new_radius]
else:
	k_values = [k_2, k_1]
	r_values = [new_radius, radius1]
	
critical = False
	
#Continuous testing and interpolation until 
while not critical:
	new_radius = np.interp(1.00, k_values, r_values)
	adjust_radii(prob, 'Inner Sphere', '1 so '+str(new_radius))
	if outer_radius1 is not None:
		adjust_radii(prob, 'Outer Sphere', '*2 so '+str(outer_radius1+new_radius))
	os.system('rm outp && rm runtpe && rm srctp')
	print("Running MCNP Test #",test_num)
	test_num += 1
	os.system('mcnp6 i=/Users/raptor/Classes/NE-156/Homework-2/'+prob+'.txt tasks 4 >/dev/null 2>&1')
	k_new = find_k()
	print('Found k value of:',k_new)
	if k_new > 0.9995 and k_new < 1.0005:
		print("This leaves a critical radius of:",new_radius)
		m_crit = density*(4/3*math.pi*(new_radius)**3)
		print('With a density of '+str(density)+', this gives us a critical mass of: '+str(round(m_crit/1000,3))+'kg')
		sys.exit()
		
	if k_new < k_values[0]:
		k_values = [k_new, k_values[0]]
		r_values = [new_radius, r_values[0]]
	elif k_new > k_values[0] and k_new < 1.0:
		k_values = [k_new, k_values[0]]
		r_values = [new_radius, r_values[0]]
	elif k_new > 1.0 and k_new < k_values[1]:
		k_values = [k_values[0], k_new]
		r_values = [r_values[0], new_radius]
	elif k_new > k_values[1]:
		k_values = [k_values[0], k_new]
		r_values = [r_values[0], new_radius]
