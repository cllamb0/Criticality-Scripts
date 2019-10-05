from critical_mass import critical as crit
import argparse
import numpy as np
import math
import os

def adjust_input(problem, locator, new_text):
	with open('/Users/raptor/Classes/NE-156/Homework-2/'+problem+'.txt', 'r') as filename:
		linedata = filename.readlines()
	for i, line in enumerate(linedata):
		if locator in line:
			linedata[i] = new_text+'          $ '+locator+'\n'
	with open('/Users/raptor/Classes/NE-156/Homework-2/'+problem+'.txt', 'w') as filename:
		filename.writelines(linedata)

parser = argparse.ArgumentParser()
parser.add_argument(
	'--problem', '-p', type=str, default=None, help=('Enter a number corresponding '+
	'to the problem that you are working on.'))
parser.add_argument(
	'--save_radius', '-s', action='store_true', default=False, help=('Saves radius as output if flagged'))

args = parser.parse_args()
arg_dict = vars(args)

prob = arg_dict['problem']
save = arg_dict['save_radius']

if '5' not in prob:
	crit(prob, save)
else:
	atom_fracs = np.linspace(0.000661, 0.000663, 21) 
	critical_radii, critical_masses, concentrations, densities = [], [], [], []
	m_pu239, n_a = 239.0521636, 6.022*10**23
	m_h, m_o = 1.00784, 15.99903
	n_h20L = (1000*n_a)/(2*m_h+m_o)
	for pu_frac in atom_fracs:
		concentraion = (pu_frac*(m_pu239*n_h20L))/(n_a*(1-pu_frac))
		print('Trying out Pu-239 atom fraction of: '+str(pu_frac)+' ('+str(round(concentraion,3))+'g/L)')
		mixed_density = 1+(concentraion/1000)
		h_frac = (2/3)*(1-pu_frac)
		o_frac = (1/3)*(1-pu_frac)
		w_per = (pu_frac*m_pu239)/((pu_frac*m_pu239)+((1-pu_frac)*(2*m_h+m_o)))
		input_text = 'm1 94239 '+str(pu_frac*100)+' 1001 '+str(h_frac*100)+' 8016 '+str(o_frac*100)
		adjust_input('5', 'Pu-H2O Solution', input_text)
		adjust_input('5', 'Inner Sphere', '1 so 21.5')
		adjust_input('5', 'sphere of Solution' , '1 1 -'+str(mixed_density)+'  -1     imp:n=1')
		ri_crit, mi_crit = crit('5',True)
		critical_radii.append(ri_crit)
		critical_masses.append((mi_crit*w_per))
		concentrations.append(concentraion)
		densities.append(mixed_density)
	min_crit_mass, min_crit_radius = min(critical_masses), critical_radii[np.argmin(critical_masses)]
	min_crit_pufrac, min_crit_concentration = atom_fracs[np.argmin(critical_masses)], concentrations[np.argmin(critical_masses)]
	final_input = 'm1 94239 '+str(min_crit_pufrac*100)+' 1001 '+str(((2/3)*(1-min_crit_pufrac))*100)+' 8016 '+str(((1/3)*(1-min_crit_pufrac))*100)
	adjust_input('5', 'Pu-H2O Solution', final_input)
	adjust_input('5', 'Inner Sphere', '1 so '+str(min_crit_radius))
	adjust_input('5', 'sphere of Solution' , '1 1 -'+str(densities[np.argmin(critical_masses)])+'  -1     imp:n=1')
	print('Found minimum, rerunning to save proper output.')
	x, y = crit('5',True)
	print('The minimum calculated critical mass of the solution was: '+str(round((min_crit_mass/1000),3))+'kg')
	print('This happened at a radius of: '+str(round(min_crit_radius,3))+'cm')
	#print('With a volume of: '+str(round(((4/3)*math.pi*(min_crit_radius)**3),3))+'cm^3')
	print('And a Pu-239 fraction of: '+str(min_crit_pufrac))
	print('This is a concentration of: '+str(round(min_crit_concentration,3))+'g/L')
