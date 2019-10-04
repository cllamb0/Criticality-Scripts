import os
import sys
import math
import numpy as np
import argparse

def critical(prob, save):
	def vprint(save, text):
		if save:
			pass
		else:
			print(text)
		
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
					radius = float(line[5:].rstrip('$ Inner Sphere\n'))
			if locator2 is not None:
				for line in lines:
					if locator2 in line:
						outer_radius = float(line[5:].rstrip('$ Outer Sphere\n')) - radius
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

	if prob == None:
		print('Please enter what problem you are working on!')
		sys.exit()
	#prob = input('What Problem are you working on? ')

	with open(prob+'.txt', 'r') as filename:
		lines = filename.readlines()
		if '5' not in prob:
			density = float(lines[1][5:12].strip())
		else:
			density = float(lines[1][5:7].strip())
		
	del lines

	test_num=1
	os.chdir('Outputs/Prob'+prob[0]+'/'+prob+'/')

	try:
		os.system('rm outp && rm runtpe && rm srctp')
	except:
		pass
		
	vprint(save, "Running MCNP Test # "+str(test_num))
	test_num += 1
	try:
		os.system('mcnp6 i=/Users/raptor/Classes/NE-156/Homework-2/'+prob+'.txt tasks 7 >/dev/null 2>&1')
	except Exception as e:
		print(e)
		print("Likely an error with some formatting in the MCNP input, check that and try again.")
		sys.exit()
	k_1 = find_k()
	radius1, outer_radius1 = find_radii(prob,'Inner Sphere', 'Outer Sphere')

	#Begin adjustments if necessary
	print('Found k value of: '+str(k_1))
	if k_1 > 0.9995 and k_1 < 1.0005:
		vprint(save, "This leaves a critical radius of: "+str(radius1))
		m_crit = density*(4/3*math.pi*(radius1)**3)
		vprint(save, 'With a density of '+str(density)+', this gives us a critical mass of: '+str(round(m_crit/1000,3))+'kg')
		if save:
			os.chdir('/Users/raptor/Classes/NE-156/Homework-2/')
			return radius1, m_crit
		else:
			sys.exit()

	#Far away runs of MCNP
	new_radius, io_rad = find_radii(prob, 'Inner Sphere', 'Outer Sphere')
		
	far_from_critical, second = True, True
		
	while far_from_critical:
		if second:
			if k_1 >= 1:
				if new_radius > 1:
					new_radius = new_radius - 1
				else:
					new_radius = 0.5*new_radius
			elif k_1 <= 1:
				new_radius = new_radius + 1
			second = False
		adjust_radii(prob, 'Inner Sphere', '1 so '+str(new_radius))
		if outer_radius1 is not None:
			adjust_radii(prob, 'Outer Sphere', '2 so '+str(outer_radius1+new_radius))
		os.system('rm outp && rm runtpe && rm srctp')
		vprint(save, "Running MCNP Test # "+str(test_num))
		test_num += 1
		os.system('mcnp6 i=/Users/raptor/Classes/NE-156/Homework-2/'+prob+'.txt tasks 7 >/dev/null 2>&1')
		k_2 = find_k()
		print('Found k value of: '+str(k_2))
		if k_2 > 0.9995 and k_2 < 1.0005:
			vprint(save, "This leaves a critical radius of: "+str(radius1))
			m_crit = density*(4/3*math.pi*(new_radius)**3)
			vprint(save, 'With a density of '+str(density)+', this gives us a critical mass of: '+str(round(m_crit/1000,3))+'kg')
			if save:
				os.chdir('/Users/raptor/Classes/NE-156/Homework-2/')
				return new_radius, m_crit
			else:
				sys.exit()
		
		if k_2 <= 0.94 and k_1 < 1:
			new_radius = new_radius + 1
		elif k_2 >= 0.94 and k_2 < 1 and k_1 < 1:
			new_radius = new_radius + 1
		elif k_2 <= 1.06 and k_2 > 1 and k_1 < 1:
			far_from_critical = False
			break
		elif k_2 >= 1.06 and k_1 < 1:
			k_values = [k_1, k_2]
			r_values = [radius1, new_radius]
			new_radius = np.interp(1.00, k_values, r_values)
		elif k_2 <= 0.94 and k_1 > 1:
			k_values = [k_2, k_1]
			r_values = [new_radius, radius1]
			new_radius = np.interp(1.00, k_values, r_values)
		elif k_2 >= 0.94 and k_2 < 1 and k_1 > 1:
			far_from_critical = False
			break
		elif k_2 <= 1.06 and k_2 > 1 and k_1 > 1:
			if new_radius <= 1:
				new_radius = 0.5*new_radius
			else:
				new_radius = new_radius - 1
		elif k_2 <= 1.06 and k_1 > 1:
			if new_radius <= 1:
				new_radius = 0.5*new_radius
			else:
				new_radius = new_radius - 1
			
	if k_2 > k_1:
		k_values = [k_1, k_2]
		r_values = [radius1, new_radius]
	else:
		k_values = [k_2, k_1]
		r_values = [new_radius, radius1]

	critical, k_repeat = False, 0
		
	#Continuous testing and interpolation until 
	while not critical:
		new_radius = np.interp(1.00, k_values, r_values)
		adjust_radii(prob, 'Inner Sphere', '1 so '+str(new_radius))
		if outer_radius1 is not None:
			adjust_radii(prob, 'Outer Sphere', '2 so '+str(outer_radius1+new_radius))
		os.system('rm outp && rm runtpe && rm srctp')
		vprint(save, "Running MCNP Test # "+str(test_num))
		test_num += 1
		os.system('mcnp6 i=/Users/raptor/Classes/NE-156/Homework-2/'+prob+'.txt tasks 7 >/dev/null 2>&1')
		k_new = find_k()
		print('Found k value of: '+str(k_new))
		if k_new > 0.9995 and k_new < 1.0005:
			vprint(save, "This leaves a critical radius of: "+str(new_radius))
			m_crit = density*(4/3*math.pi*(new_radius)**3)
			vprint(save, 'With a density of '+str(density)+', this gives us a critical mass of: '+str(round(m_crit/1000,3))+'kg')
			if save:
				os.chdir('/Users/raptor/Classes/NE-156/Homework-2/')
				return new_radius, m_crit
			else:
				sys.exit()
			
		if k_new == k_values[0] or k_new == k_values[1]:
			k_repeat += 1
		else:
			k_repeat = 0
			
		if k_new < k_values[0]:
			k_values = [k_new, k_values[1]]
			r_values = [new_radius, r_values[1]]
		elif k_new > k_values[0] and k_new < 1.0:
			k_values = [k_new, k_values[1]]
			r_values = [new_radius, r_values[1]]
		elif k_new > 1.0 and k_new < k_values[1]:
			k_values = [k_values[0], k_new]
			r_values = [r_values[0], new_radius]
		elif k_new > k_values[1]:
			k_values = [k_values[0], k_new]
			r_values = [r_values[0], new_radius]	
		elif k_new == k_values[0]:
			k_values = [k_new, k_values[1]]
			r_values = [new_radius, r_values[1]]
		elif k_new == k_values[1]:
			k_values = [k_values[0], k_new]
			r_values = [r_values[0], new_radius]
		
		if k_new == k_values[0] and k_new == k_values[1]:
			vprint(save, 'Interpolating between a single value, gonna get nowhere')
			vprint(save, 'Found k value of: '+str(k_new))
			vprint(save, "This leaves a radius of: "+str(new_radius))
			m_crit = density*(4/3*math.pi*(new_radius)**3)
			vprint(save, 'With a density of '+str(density)+', this gives us a mass of: '+str(round(m_crit/1000,3))+'kg')
			sys.exit()
			
		if k_repeat == 3:
			vprint(save, "Stuck without changing values of k, breaking the loop")
			vprint(save, "Got stuck interpolating between:")
			vprint(save, "k values of:"+str(k_values))
			vprint(save, "r values of:"+str(r_values))
			vprint(save, "This leaves a radius of: "+str(new_radius))
			m_crit = density*(4/3*math.pi*(new_radius)**3)
			vprint(save, 'With a density of '+str(density)+', this gives us a mass of: '+str(round(m_crit/1000,3))+'kg')
			sys.exit()


