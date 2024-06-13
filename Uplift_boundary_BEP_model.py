# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 18:10:05 2024

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


num_cracks = 4 # specified number of cracks wanted
x_polder_start = 91.9+0.1
x_polder_end = 96.6
z_surface = 0.5
z_crack_mid = 0
#start, mid, end, width_mid_dict = crack_generator(num_cracks,  x_polder_start, x_polder_end,z_surface)

lista = [[92.22275089807523, 94.39336304370802, 94.49291905962735, 94.701568996672, 94.8814343162321, 95.11026374977439]
,
[92.22717331069363, 94.39949180860478, 94.49623377146345, 94.70631602010734, 94.89025797029507, 95.12868063711315]
,
[92.23159572331201, 94.40562057350155, 94.49954848329955, 94.7110630435427, 94.89908162435803, 95.1470975244519]
,
{94.49623377146345: 0.006629423672197305, 94.70631602010734: 0.009494046870694073, 94.89025797029507: 0.017647308125933375, 94.39949180860478: 0.01225752979352665, 92.22717331069363: 0.008844825236779999, 95.12868063711315: 0.036833774677510464}
]

start = lista[0]
mid =lista[1]
end =lista[2]
width_mid_dict =lista[3]

r = 5

crack_width = width_mid_dict.get(mid[r])

print(start)
print(mid)
print(end)
print(width_mid_dict)


head_up = (((crack_width*0.5*20*1000)/crack_width)/100000)*10.197
print(head_up)

#3. Create layers and mesh properties
levee_mesh_size = 2
aquifer_mesh_size = 2
cracked_layer_mesh_size = 0.2
blanket_mesh_size = 2

aquifer = [Point(x=150, z=0), Point(x=150, z=-30), Point(x=0, z=-30),
           Point(x=0, z=0),Point(x=44.9, z=0), Point(x=91.9, z=0),
           Point(x=start[r], z=0), Point(x=end[r], z=0)
           ]
"""
for i in range(0, len(mid)):
    coordinate = Point(x=start[i], z=0)
    aquifer.append(coordinate) 
    coordinate = Point(x=end[i], z=0)
    aquifer.append(coordinate) 
"""
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
             Point(x=start[r], z=0.5),
             Point(x=start[r], z=0),
             Point(x=91.9, z=0)]
pre_layer_id = dm.add_layer(pre_layer, "B_k", "Blanket")
dm.add_meshproperties(blanket_mesh_size, "Blanket Mesh", 0, pre_layer_id)

crack_layer = [Point(x=start[r], z=0.5),
             Point(x=start[r], z=0.),
             Point(x=end[r], z=0),
             Point(x=end[r], z=0.5)]
crack_layer_id = dm.add_layer(crack_layer, "B_k", "Cracked Layer")
dm.add_meshproperties(cracked_layer_mesh_size, "Cracked Layer Mesh", 0, crack_layer_id)
                   

post_layer =[Point(x=end[r], z=0),
   Point(x=end[r], z=0.5),
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
    Point(x=start[r], z=0),
    Point(x=end[r], z=0)],
    head_up,
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
        Points=[PersistablePoint(X=start[r], Z=0), PersistablePoint(X=44.9, Z=0)]))

# Set the river boundary to be the critical boundary condition
dm.set_critical_head_boundary_condition(boundary_condition_id=river_boundary_id)

# Set the critical head search parameters
dm.set_critical_head_search_parameters(
    minimum_head_level=4.45, maximum_head_level=7, step_size=0.01,
)

from pathlib import Path

dm.serialize(Path("cracked_test_model.flox"))
dm.execute()            

results = {}

results_CriticalHead= dm.get_result(scenario_index=0, calculation_index=0)
results["Critical Head"] = results_CriticalHead.CriticalHead
results["Pipe Length"] = results_CriticalHead.PipeLength
results["Pipe Length Trajectory"] = start[r]-44.9
print(results)