# -*- coding: utf-8 -*-
"""
Created on Mon May 20 12:50:53 2024

@author: ahemp
"""

#1. Import
import random
import numpy as np
from geolib.geometry import Point

from geolib.models.dgeoflow import DGeoFlowModel
dm = DGeoFlowModel()
from geolib.models.dgeoflow.internal import CalculationTypeEnum

dm.set_calculation_type(scenario_index=0, calculation_index=0, calculation_type=CalculationTypeEnum.CRITICAL_HEAD)


#2 Modify Soil
from geolib.soils import Soil

# add soil
soil = Soil()
soil.name = "Modified Sand"
soil.code = "Mod_s"
soil.storage_parameters.horizontal_permeability = 25
soil.storage_parameters.vertical_permeability = 25
soil_sand_id = dm.add_soil(soil)

soil = Soil()
soil.name = "Modified Clay"
soil.code = "Mod_k"
soil.storage_parameters.horizontal_permeability = 0.05
soil.storage_parameters.vertical_permeability = 0.05

soil_clay_id = dm.add_soil(soil)

soil = Soil()
soil.name = "Blanket Clay"
soil.code = "B_k"
soil.storage_parameters.horizontal_permeability = 0.002
soil.storage_parameters.vertical_permeability = 0.002
soil_clay_id = dm.add_soil(soil)

def crack_generator(n, x_polder_start, x_polder_end,z_surface):
    """
    def space():
        num_samples = 4000  
        space_mean = 4.1964
        space_sigma = 0.906
        #found = False
    
        while True:
            spacing = (np.random.lognormal(mean=space_mean, sigma=space_sigma, size=num_samples))/100 #in meters
            value = spacing[1]
            #print(f"Generated value: {value}")
            if 1.22 <= value <= 2.12:
                break  
        return value
    """
    def space():
        num_samples = 4000  # Adjust the number of samples as needed
        space_mean = 4.1964
        space_sigma = 0.906
        spacing = (np.random.lognormal(mean=space_mean, sigma=space_sigma, size=num_samples))/100 #in meters
        return spacing[1]
    
    def width():
        num_samples = 4000
        width_mean = -4.4607
        width_sigma = 0.5973
        
        while True: 
           widths = np.random.lognormal(mean=width_mean, sigma=width_sigma, size=num_samples)
           value = widths[1]
           if 0.012 <= value <= 0.017:
               break
        return value
    """"
    def width():
        num_samples = 4000
        width_mean = -4.4607
        width_sigma = 0.5973
        widths = np.random.lognormal(mean=width_mean, sigma=width_sigma, size=num_samples)
        return widths[1]
    """
   
    def define_crack_back( x_crack_end_1,Space,Width):
        x_crack_strt = float(x_crack_end_1 + Space)
        x_crack_end = float((x_crack_strt)+Width)
        x_crack_mid = float(x_crack_strt+(Width/2))
        return x_crack_strt, x_crack_end, x_crack_mid
    
    def define_crack_front(x_crack_strt_1,Space,Width):
        x_crack_end = float(x_crack_strt_1 - Space)
        x_crack_strt = float((x_crack_end)-Width)
        x_crack_mid = float(x_crack_strt+(Width/2))
        return x_crack_strt, x_crack_end, x_crack_mid
    

    num_cracks = n 
    
    # Define crack 1
    width1 = width()
    x1_crack_start = float(np.random.uniform(x_polder_start, x_polder_end))
    x1_crack_end = float((x1_crack_start)+width1)
    x1_crack_mid = float(x1_crack_start+(width1/2))
    
    x_crack_start = x1_crack_start
    x_crack_end = x1_crack_end
    
    # Crack coordinate lists
    x_start_points = [x1_crack_start,]
    x_mid_points = [x1_crack_mid, ]
    x_end_points = [x1_crack_end, ]
    
    width_mid_dict = {x1_crack_mid:width1}
    
    #Loop to generate the cracks considering spacing and width
    while (len(x_end_points)) < num_cracks:

    #for i in range(0,num_cracks+1):
        #Choice between the crack being behind or in front of the previously generated crack
        choice = random.choice(['Front', 'Back'])  
        #different spacing and width per crack
        
        Width = width()
        Space = space()
        
        
        if choice == 'Back':
            x_crack_strt_rslt, x_crack_end_rslt, x_crack_mid_rslt = define_crack_back(x_crack_end,Space,Width)
            #IF statement to make sure the crack is in the polder, if not cracks not considered
            if (x_crack_end_rslt > x_polder_end) or (x_crack_strt_rslt >x_polder_end):
                x_crack_end = x_crack_end
                
            else:
                x_start_points.append(x_crack_strt_rslt)
                x_mid_points.append(x_crack_mid_rslt)
                x_end_points.append(x_crack_end_rslt)
                x_crack_end = x_crack_end_rslt
                
                width_mid_dict[x_crack_mid_rslt] = Width
        elif choice == "Front":
            x_crack_strt_rslt, x_crack_end_rslt, x_crack_mid_rslt = define_crack_front(x_crack_start, Space, Width)
            if (x_crack_strt_rslt < x_polder_start) or (x_crack_end_rslt < x_polder_start):
                x_crack_start = x_polder_start
            
            else:
                x_start_points.append(x_crack_strt_rslt)
                x_mid_points.append(x_crack_mid_rslt)
                x_end_points.append(x_crack_end_rslt)
                x_crack_start = x_crack_strt_rslt
                width_mid_dict[x_crack_mid_rslt] = Width
                
        #i = i + 1         
    #sort the coordintes so they can be easily inputed into dg Flow            
    x_start_points.sort()
    x_mid_points.sort()
    x_end_points.sort()
    return x_start_points, x_mid_points, x_end_points, width_mid_dict

num_cracks = 4 # specified number of cracks wanted
x_polder_start = 91.9+0.1
x_polder_end = 97#96.6
z_surface = 0.5
z_crack_mid = 0
start, mid, end, width_mid_dict = crack_generator(num_cracks,  x_polder_start, x_polder_end,z_surface)

r = 0 #set the crack which you want to consider as exit point with first one being 0

print(start)
print(",")
print(mid)
print(",")
print(end)
print(",")
print(width_mid_dict)

mid_width_max = max(width_mid_dict, key = width_mid_dict.get)
#print(mid_width_max)

max_width = max(width_mid_dict.values())

#3. Create layers and mesh properties
levee_mesh_size = 2
aquifer_mesh_size = 2
cracked_layer_mesh_size = 0.2
blanket_mesh_size = 2

aquifer = [Point(x=end[len(end)-1]+0.1, z=0),Point(x=150, z=0), Point(x=150, z=-30), 
           Point(x=0, z=-30),Point(x=0, z=0),Point(x=44.9, z=0), Point(x=91.9, z=0), 
           Point(x=start[0]-0.1, z=0),]

for i in range(0, len(mid)):
    coordinate = Point(x=mid[i], z=0)
    aquifer.append(coordinate) 
aquifer_id = dm.add_layer(aquifer, "Mod_s", "Aquifer")
dm.add_meshproperties(aquifer_mesh_size, "Aquifer Mesh", 0, aquifer_id)


levee = [Point(x=44.9, z=0), 
         Point(x=64.4, z=7),
         Point(x=72.4, z=7),
         Point(x=91.8, z=0.5),
         Point(x=91.9, z=0)]
levee_id = dm.add_layer(levee, "H_Rk_k_shallow", "Levee")
dm.add_meshproperties(levee_mesh_size, "Levee Mesh", 0, levee_id)

pre_layer = [Point(x=91.8, z=0.5),
             Point(x=start[0]-0.1, z=0.5),
             Point(x=start[0]-0.1, z=0),
             Point(x=91.9, z=0)]
pre_layer_id = dm.add_layer(pre_layer, "B_k", "Blanket")
dm.add_meshproperties(blanket_mesh_size, "Blanket Mesh", 0, pre_layer_id)

pre_crack_layer = [Point(x=start[0]-0.1, z=0.5),
             Point(x=start[0], z=0.5),
             Point(x=mid[0], z=0),
             Point(x=start[0]-0.1, z=0)]
pre_crack_layer_id = dm.add_layer(pre_crack_layer, "Mod_k", "Cracked Layer")
dm.add_meshproperties(cracked_layer_mesh_size, "Cracked Layer Mesh", 0, pre_crack_layer_id)
                   
for i in range(1, len(end)):
        layer = [Point(x=mid[i-1], z=0),
               Point (x=end[i-1], z=0.5),
               Point(x=start[i], z=0.5),
               Point(x=mid[i], z=0)]
        layer_id = dm.add_layer(layer, "Mod_k", "Cracked Layer")
        dm.add_meshproperties(cracked_layer_mesh_size, "Cracked Layer Mesh", 0, layer_id)
        
post_crack_layer = [Point(x=mid[len(mid)-1], z=0),
    Point(x=end[len(end)-1], z=0.5),
    Point(x=end[len(end)-1]+0.1, z=0.5),
    Point(x=end[len(end)-1]+0.1, z=0)]
post_crack_layer_id = dm.add_layer(post_crack_layer, "Mod_k", "Cracked Layer")
dm.add_meshproperties(cracked_layer_mesh_size, "Cracked Layer Mesh", 0, post_crack_layer_id)


post_layer =[Point(x=end[len(end)-1]+0.1, z=0),
   Point(x=end[len(end)-1]+0.1, z=0.5),
   Point(x=150, z=0.5),
   Point(x=150, z=0)]
post_layer_id = dm.add_layer(post_layer, "B_k", "Blanket")
dm.add_meshproperties(blanket_mesh_size, "Blanket Mesh", 0, post_layer_id)


#4. Set Boundaries
river_boundary_id = dm.add_boundary_condition([
    Point(x=0, z=0),
    Point(x=44.9, z=0),
    Point(x=64.4, z=7)],
    5,
    "River"
)

dm.add_boundary_condition([
    Point(x=150, z=0), 
    Point(x=150, z=-30)],
    0,
    "Polder"
)


dm.add_boundary_condition([
    Point(x=start[0], z=0.5),
    Point(x=mid[0], z=0),
    Point(x=end[0], z=0.5)],
    0,
    "Crack"
)

#5. Set Pipe trajectory
from geolib.models.dgeoflow.internal import PipeTrajectory, ErosionDirectionEnum, PersistablePoint

dm.set_pipe_trajectory(
    pipe_trajectory=PipeTrajectory(
        Label="Pipe",
        D70=0.3,
        ErosionDirection=ErosionDirectionEnum.RIGHT_TO_LEFT,
        ElementSize=1,
        Points=[PersistablePoint(X=mid[0], Z=0), PersistablePoint(X=44.9, Z=0)]))

# Set the river boundary to be the critical boundary condition
dm.set_critical_head_boundary_condition(boundary_condition_id=river_boundary_id)

# Set the critical head search parameters
dm.set_critical_head_search_parameters(
    minimum_head_level=3.2, maximum_head_level=4, step_size=0.01,
)

from pathlib import Path

dm.serialize(Path("cracked_test_model.flox"))
dm.execute()            

results = {}

results_CriticalHead= dm.get_result(scenario_index=0, calculation_index=0)
results["Critical Head"] = results_CriticalHead.CriticalHead
results["Pipe Length"] = results_CriticalHead.PipeLength
results["Pipe Length Trajectory"] = mid[0]-44.9
print(results)