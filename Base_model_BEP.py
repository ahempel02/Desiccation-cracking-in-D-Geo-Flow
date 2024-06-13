# -*- coding: utf-8 -*-
"""
Created on Mon May 20 11:16:25 2024

@author: ahemp
"""
#1. Import
from geolib.models.dgeoflow import DGeoFlowModel

dm = DGeoFlowModel()

from geolib.models.dgeoflow.internal import CalculationTypeEnum

dm.set_calculation_type(calculation_type=CalculationTypeEnum.CRITICAL_HEAD)

#2 Modify Soil
from geolib.soils import Soil

# add soil
soil = Soil()
soil.name = "Modified Clay"
soil.code = "Mod_k"
soil.storage_parameters.horizontal_permeability = 0.002
soil.storage_parameters.vertical_permeability = 0.002
soil_clay_id = dm.add_soil(soil)

soil = Soil()
soil.name = "Modified Sand"
soil.code = "Mod_s"
soil.storage_parameters.horizontal_permeability = 25
soil.storage_parameters.vertical_permeability = 25
soil_sand_id = dm.add_soil(soil)

#3. Create layers
from geolib.geometry import Point

delta = 0
h1 = 91.8+delta
h2 = 91.9+delta
h3 = 92+delta
h4 = 92.1+delta

# add layers
aquifer = [
    Point(x=0, z=-30),
    Point(x=0, z=0),
    Point(x=44.9, z=0),
    Point(x=h2, z=0),
    Point(x=h3, z=0),
    Point(x=150, z=0),
    Point(x=150, z=-30), 
] 
aquifer_id = dm.add_layer(aquifer, "Mod_s", "Aquifer")
dm.add_meshproperties(2, "Aquifer Mesh", 0, aquifer_id)

levee = [Point(x=44.9, z=0), 
         Point(x=64.4, z=7),
         Point(x=72.4, z=7),
         Point(x=h1, z=0.5),
         Point(x=h2, z=0),
]
levee_id = dm.add_layer(levee, "H_Rk_k_shallow", "Levee")
dm.add_meshproperties(2, "Levee Mesh", 0, levee_id)

blanket = [Point(x=h3, z=0),
           Point(x=h4, z=0.5),
           Point(x=150, z=0.5),
           Point(x=150, z=0),
]
blanket_id = dm.add_layer(blanket, "Mod_k", "Blanket")
dm.add_meshproperties(2, "Blanket Mesh", 0, blanket_id)

layers_and_soils = [
    (aquifer, "Mod_s", "Aquifer"),
    (levee, "Mod_k", "Levee"),
    (blanket, "Mod_k", "Blanket"),
]

#[dm.add_layer(points, soil, label) for points, soil, label in layers_and_soils]

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
    Point(x=h2, z=0),
    Point(x=h3, z=0)],
    0,
    "Heave"
)

#5. Set Pipe trajectory
from geolib.models.dgeoflow.internal import PipeTrajectory, ErosionDirectionEnum, PersistablePoint

dm.set_pipe_trajectory(
    pipe_trajectory=PipeTrajectory(
        Label="Pipe",
        D70=0.3,
        ErosionDirection=ErosionDirectionEnum.RIGHT_TO_LEFT,
        ElementSize=1,
        Points=[PersistablePoint(X=h2, Z=0), PersistablePoint(X=44.9, Z=0)]))

# Set the river boundary to be the critical boundary condition
dm.set_critical_head_boundary_condition(boundary_condition_id=river_boundary_id)

# Set the critical head search parameters
dm.set_critical_head_search_parameters(
    minimum_head_level=0, maximum_head_level=7, step_size=0.01,
)

from pathlib import Path

dm.serialize(Path("uncracked_test_model.flox"))
dm.execute()            

results = {}

results_CriticalHead= dm.get_result(scenario_index=0, calculation_index=0)
results["Critical Head"] = results_CriticalHead.CriticalHead

print(results)