################################
# Planets Enhanced Engine v2.0 #
#       Synergy Triggers 	   #
################################
#
#	### general planet/system checks	
#
#	is_gas_giant = yes/no #planet scope	
#   is_gas_giant_moon = yes/no #planet scope
#	is_primitive_planet = yes/no #planet/pop scope - uses owner
#	is_fallen_empire_planet = yes/no #planet/pop scope - uses owner
#	is_presapient_planet = yes/no #planet scope - checks any_pop
#	is_sol_system_planet = yes/no #planet scope - checks solar_system
#	regular_star_system = yes/no - means the system has a single star
#	binary_star_system = yes/no - 2 stars in the system
#	ternary_star_system = yes/no - 3 stars in the system
#	
#
#	### species class checks
#
#	is_presapient_pop = yes/no #pop scope
#	is_arthropoid = yes/no #pop scope	 
#	is_mammalian = yes/no #pop scope	 
#	is_avian = yes/no #pop scope	 
#	is_reptilian = yes/no #pop scope	 
#	is_fungoid = yes/no #pop scope	 
#	is_molluscoid = yes/no #pop scope	 
#	is_humanoid = yes/no #pop scope	 
#	is_plantoid = yes/no #pop scope	 
#
#
### Vanilla Star Classes - these triggers will always have an effect
## --- > orbit trigger check, all of these have solar_system scope in the trigger
#		 example: orbits_star_class_sc_a = { solar_system = { is_star_class_sc_a = yes } }
#
#     orbits_star_class_sc_b = yes/no  
#     orbits_star_class_sc_a = yes/no 
#     orbits_star_class_sc_f = yes/no 
#     orbits_star_class_sc_g = yes/no 
#     orbits_star_class_sc_k = yes/no 
#     orbits_star_class_sc_m = yes/no 
#     orbits_sc_black_hole = yes/no 
#     orbits_sc_neutron_star = yes/no 
#     orbits_sc_pulsar = yes/no 
#
### Real Space Star Classes - these triggers will only have an effect when Real Space is present
## --- > base star_class checks
#     is_star_class_sc_o = yes/no
#     is_star_class_sc_o_super = yes/no
#     is_star_class_sc_o_hyper = yes/no
#     is_star_class_sc_b_super = yes/no
#     is_star_class_sc_a_super = yes/no
#     is_star_class_sc_f_super = yes/no
#     is_star_class_sc_g_giant = yes/no
#     is_star_class_sc_g_super = yes/no
#     is_star_class_sc_k_giant = yes/no
#     is_star_class_sc_k_super = yes/no
#     is_star_class_sc_m_giant = yes/no
#     is_star_class_sc_m_super = yes/no
#     is_star_class_sc_m_hyper = yes/no
#     is_star_class_sc_l = yes/no
#     is_star_class_sc_d = yes/no
#     is_star_class_sc_gm = yes/no
#     is_star_class_sc_c_giant = yes/no
#     is_star_class_sc_s_giant = yes/no
#     is_star_class_sc_w_azure = yes/no
#     is_star_class_sc_w_red = yes/no
#     is_star_class_sc_w_green = yes/no
#     is_star_class_sc_w_purple = yes/no
#     is_star_class_sc_nova_1 = yes/no
#     is_star_class_sc_nova_2 = yes/no
#     is_star_class_sc_collapsar = yes/no
#     is_star_class_sc_protostar = yes/no
#     is_star_class_sc_lbv_blue = yes/no
#     is_star_class_sc_lbv_green = yes/no
#     is_star_class_sc_lbv_red = yes/no
#     is_star_class_sc_tt_red = yes/no
#     is_star_class_sc_tt_orange = yes/no
#     is_star_class_sc_tt_white = yes/no
#     is_star_class_sc_ae = yes/no
#     is_star_class_sc_magnetar = yes/no
## --- > orbit trigger check, all of these have solar_system scope in the trigger
#     orbits_star_class_sc_o = yes/no 
#     orbits_star_class_sc_o_super = yes/no 
#     orbits_star_class_sc_o_hyper = yes/no 
#     orbits_star_class_sc_b_super = yes/no 
#     orbits_star_class_sc_a_super = yes/no 
#     orbits_star_class_sc_f_super = yes/no 
#     orbits_star_class_sc_g_giant = yes/no 
#     orbits_star_class_sc_g_super = yes/no 
#     orbits_star_class_sc_k_giant = yes/no 
#     orbits_star_class_sc_k_super = yes/no 
#     orbits_star_class_sc_m_giant = yes/no 
#     orbits_star_class_sc_m_super = yes/no 
#     orbits_star_class_sc_m_hyper = yes/no 
#     orbits_star_class_sc_l = yes/no 
#     orbits_star_class_sc_d = yes/no 
#     orbits_star_class_sc_gm = yes/no 
#     orbits_star_class_sc_c_giant = yes/no 
#     orbits_star_class_sc_s_giant = yes/no 
#     orbits_star_class_sc_w_azure = yes/no 
#     orbits_star_class_sc_w_red = yes/no 
#     orbits_star_class_sc_w_green = yes/no 
#     orbits_star_class_sc_w_purple = yes/no 
#     orbits_star_class_sc_no va_1 = yes/no 
#     orbits_star_class_sc_no va_2 = yes/no 
#     orbits_star_class_sc_collapsar = yes/no 
#     orbits_star_class_sc_protostar = yes/no 
#     orbits_star_class_sc_lbv_blue = yes/no 
#     orbits_star_class_sc_lbv_green = yes/no 
#     orbits_star_class_sc_lbv_red = yes/no 
#     orbits_star_class_sc_tt_red = yes/no 
#     orbits_star_class_sc_tt_orange = yes/no 
#     orbits_star_class_sc_tt_white = yes/no 
#     orbits_star_class_sc_ae = yes/no 
#     orbits_star_class_sc_magnetar = yes/no 
############################################
#	  Guilli's Planet Modifiers			   #
############################################

## Found on Fallen Empire worlds		[planet scope]
#has_modifier_Utopian_World = yes/no
#has_modifier_Utopian_Services = yes/no
#has_modifier_Primitive_Reserve = yes/no
#has_modifier_Unified_Processing = yes/no
#has_modifier_Planetary_Shielding_FE = yes/no
#has_modifier_Living_Infrastructure = yes/no
#has_modifier_Galactic_Databanks = yes/no
#has_modifier_Monument_To_The_Fallen = yes/no

## Found on random planets (Depending on what fits. Frequent_Thunderstorms wont ever spawn on molten worlds for example)		[planet scope]
#has_modifier_Frequent_Thunderstorms = yes/no
#has_modifier_Global_Thunderstorms = yes/no
#has_modifier_Highly_Charged_Air_Particles = yes/no
#has_modifier_Time_Displaced_Planet = yes/no
#has_modifier_Single_Biome = yes/no
#has_modifier_Hyper_Complex_Biome = yes/no
#has_modifier_Thin_Atmospheres = yes/no
#has_modifier_Dense_Atmospheres = yes/no
#has_modifier_Strong_Volcanism = yes/no
#has_modifier_weak_magnetic_field_2 = yes/no
#has_modifier_strong_magnetic_field_2 = yes/no
#has_modifier_unstable_tectonics_2 = yes/no
#has_modifier_asteroid_impacts_2 = yes/no
#has_modifier_mineral_rich_2 = yes/no
#has_modifier_ultra_rich_2 = yes/no
#has_modifier_low_gravity_2 = yes/no
#has_modifier_high_gravity_2 = yes/no
#has_modifier_Floating_Islands = yes/no
#has_modifier_Hostile_Flora = yes/no
#has_modifier_Magma_Ocean = yes/no
#has_modifier_Toxic_Gas = yes/no
#has_modifier_Extensive_Cavern_System = yes/no
#has_modifier_Titanic_Predators = yes/no
#has_modifier_Unnatural_World = yes/no			# Spawned with anomaly event
#has_modifier_Atmospheric_Stimulant = yes/no
#has_modifier_Unusual_Seasons = yes/no
#has_modifier_Perfect_Seasons = yes/no
#has_modifier_Ruined_Battlefield = yes/no
#has_modifier_Spaceship_Graveyard = yes/no
#has_modifier_Living_Planet = yes/no
#has_modifier_Gemstones = yes/no
#has_modifier_Ideal_for_Life = yes/no
#has_modifier_Endless_Fish = yes/no
#has_modifier_Artificial_Water = yes/no
#has_modifier_Clear_Skies = yes/no
#has_modifier_Android_Pleasure_Palace = yes/no
#has_modifier_Melted_Ice_Caps = yes/no
#has_modifier_Small_Islands = yes/no
#has_modifier_Windy = yes/no
#has_modifier_Simple_Organisms = yes/no
#has_modifier_Newly_Evolved_Complex_Organisms = yes/no
#has_modifier_Delicious_Ingredients = yes/no
#has_modifier_Recent_Mass_Extinction = yes/no
#has_modifier_Friendly_Wildlife = yes/no
#has_modifier_Pleasant_Weather = yes/no
#has_modifier_Unusual_Formations = yes/no
#has_modifier_Flat_Terrain = yes/no
#has_modifier_Rugged_Terrain = yes/no
#has_modifier_Many_Extremophiles = yes/no
#has_modifier_Great_Temperature_Variation = yes/no
#has_modifier_Gorgeous_Sky = yes/no
#has_modifier_Large_Asteroid = yes/no
#has_modifier_Asteroid_Moon = yes/no
#has_modifier_Ice_Age = yes/no
#has_modifier_Ancient_Temple = yes/no
#has_modifier_Metal_Asteroid = yes/no
#has_modifier_Dense_Core = yes/no
#has_modifier_Unusual_Sun_Spots = yes/no
#has_modifier_Tilted_Axis = yes/no
#has_modifier_Perpendicular_Axis = yes/no
#has_modifier_Radioactive_Mantle = yes/no
#has_modifier_Locust_Plagues = yes/no
#has_modifier_Acidic_Seas = yes/no
#has_modifier_Empathic_Life = yes/no
#has_modifier_Seasonal_Flooding = yes/no
#has_modifier_Lingering_Pollution = yes/no
#has_modifier_Thin_ozone_layer = yes/no
#has_modifier_Symbiotic_life = yes/no
#has_modifier_Resilent_parasites = yes/no
#has_modifier_Ice_Flora = yes/no
#has_modifier_Strange_Ice_River = yes/no
#has_modifier_Juggernaut_Manta_Rays = yes/no
#has_modifier_Black_Oily_Stone = yes/no
#has_modifier_Crystal_Moon_Palace = yes/no
#has_modifier_Cities_in_the_sky = yes/no
#has_modifier_Old_World = yes/no
#has_modifier_Dunes = yes/no
#has_modifier_Extensive_reef_systems = yes/no
#has_modifier_Unusual_Bright_Sun = yes/no
#has_modifier_Protomolecule_Infected_Station = yes/no			# Spawned with anomaly event
#has_modifier_Trubbles = yes/no
#has_modifier_Strange_Voices = yes/no
#has_modifier_Hot_Geysers = yes/no
#has_modifier_Cryogeysers = yes/no
#has_modifier_Very_Hot_Core = yes/no
#has_modifier_Solidified_Core = yes/no
#has_modifier_Temple_of_the_Ancient_One = yes/no
#has_modifier_Beautiful_Lakes = yes/no
#has_modifier_Proto_Forests = yes/no
#has_modifier_Dense_Forests = yes/no
#has_modifier_Planetwide_Forest = yes/no
#has_modifier_Hiveworld = yes/no
#has_modifier_Periodic_Meteor_Showers = yes/no
#has_modifier_Arachnophobia = yes/no
#has_modifier_Giant_Worm = yes/no
#has_modifier_Artificial_Core = yes/no
#has_modifier_Fast_Rotation = yes/no
#has_modifier_Exotic_Spices = yes/no
#has_modifier_Sandstorms = yes/no
#has_modifier_Sand_Tornadoes = yes/no
#has_modifier_Silicon_Crystals = yes/no
#has_modifier_Quicksand = yes/no
#has_modifier_Never_Ending_Aurora = yes/no
#has_modifier_Spirals_of_Ice = yes/no
#has_modifier_Furry_Packs = yes/no
#has_modifier_Blizzards = yes/no
#has_modifier_Abominable_Predators = yes/no
#has_modifier_Rich_Soil = yes/no
#has_modifier_Otherworldly_Colours = yes/no
#has_modifier_Misty = yes/no
#has_modifier_Ecological_Nervous_System = yes/no
#has_modifier_Carnivorous_Flies = yes/no
#has_modifier_Algae_Boom = yes/no
#has_modifier_Ocean_Forests = yes/no
#has_modifier_Warm_Water_Lakes = yes/no
#has_modifier_Torrential_Rainstorms = yes/no
#has_modifier_Ocean_Currents = yes/no
#has_modifier_Ocean_Ridges = yes/no
#has_modifier_Ocean_Trenches = yes/no
#has_modifier_Unique_Marine_Habitats = yes/no
#has_modifier_Massive_Waves = yes/no
#has_modifier_Surface_Of_Bones = yes/no
#has_modifier_Ghost_Ships = yes/no
#has_modifier_Omnious_Fog = yes/no
#has_modifier_Beautiful_Planet_Rings = yes/no
#has_modifier_Blood_Moon = yes/no
#has_modifier_Solar_Eclipse = yes/no
#has_modifier_Lunar_Dance = yes/no
#has_modifier_Dark_Skies = yes/no
#has_modifier_Musical_Creatures = yes/no
#has_modifier_Odd_Cloud_Shapes = yes/no
#has_modifier_Giant_Mold_Blobs = yes/no
#has_modifier_Subterranean_Eco_System = yes/no
#has_modifier_Colossal_Cliffs = yes/no
#has_modifier_Massive_Waterfalls = yes/no
#has_modifier_Strange_Alien_Eggs = yes/no
#has_modifier_Mushroom_Forest = yes/no
#has_modifier_Hollow_Structure = yes/no
#has_modifier_Crystallized_Structure = yes/no
#has_modifier_Abandoned_Mining_Platforms = yes/no
#has_modifier_Decaying_Structures = yes/no
#has_modifier_Toxic_Flora_Fauna = yes/no
#has_modifier_Water_Pockets = yes/no
#has_modifier_Lava_Geysers = yes/no
#has_modifier_Thin_Planetary_Crust = yes/no
#has_modifier_Hydrogen_Mist = yes/no
#has_modifier_Spherical_Asteroid = yes/no
#has_modifier_Binary_Asteroids = yes/no
#has_modifier_Trojan_Asteroid = yes/no
#has_modifier_C-type_Asteroid = yes/no
#has_modifier_S-type_Asteroid = yes/no
#has_modifier_M-type_Asteroid = yes/no
#has_modifier_V-type_Asteroid = yes/no
#has_modifier_Corrosive_Atmosphere = yes/no
#has_modifier_Toxic_Garbage = yes/no
#has_modifier_Hydrogen_Ice = yes/no
#has_modifier_Nitrogen_Ice = yes/no
#has_modifier_Cracking_Surface = yes/no
#has_modifier_Chlorine_Planet = yes/no
#has_modifier_Phosphorus_Planet = yes/no
#has_modifier_Sulfur_Planet = yes/no
#has_modifier_Deep_Aquifer = yes/no
#has_modifier_Iron_Planet = yes/no
#has_modifier_Carbon_Planet = yes/no
#has_modifier_Stellar_Irradiation = yes/no
#has_modifier_Iron_Rich = yes/no
#has_modifier_Titanium_Rich = yes/no
#has_modifier_Gold_Rich = yes/no
#has_modifier_Platinum_Rich = yes/no
#has_modifier_Mercury_Atmosphere = yes/no
#has_modifier_Cobalt_Rich = yes/no
#has_modifier_Lithium_Rich = yes/no
#has_modifier_Acid_Rain = yes/no
#has_modifier_Salt_Flats = yes/no
#has_modifier_Cursed_world = yes/no
#has_modifier_Garbage_Dump = yes/no
#has_modifier_Abundant_Natural_Radioactivity = yes/no
#has_modifier_Proto_Planet = yes/no
#has_modifier_Sunken_Cities = yes/no
#has_modifier_Titanic_Geo_Form = yes/no
#has_modifier_Singing_Star = yes/no
#has_modifier_Precursor_Star_Filter = yes/no
#has_modifier_Wretched_Abyss = yes/no
#has_modifier_Resonant_Twins = yes/no
#has_modifier_Extinct_Species = yes/no

## Stars modifiers		[planet scope]
#has_modifier_Low_Metallicity = yes/no
#has_modifier_High_Metallicity = yes/no
#has_modifier_Plasmoid_Life = yes/no
#has_modifier_Plasma_Tornadoes = yes/no
#has_modifier_Stellar_Spectacle = yes/no
#has_modifier_Solar_Storm = yes/no
#has_modifier_Violent_Sun = yes/no

## Spawned on stars + all planets in the star's system (timed repeating event)		[planet scope]
#has_modifier_Increased_Solar_Output = yes/no			## All system planets
#has_modifier_Decreased_Solar_Output = yes/no
#has_modifier_Increased_Solar_Activity = yes/no			## Star
#has_modifier_Decreased_Solar_Activity = yes/no

## Neutron Stars modifiers		[planet scope]
#has_modifier_Compact_Star = yes/no

## Pulsars modifiers
#has_modifier_Pulsar_clock = yes/no			# Spawned with anomaly event		[planet scope]

## Black holes modifiers		[planet scope]
#has_modifier_Inspirational = yes/no

# Spawns on planets with a wondrous tileblocker (wonderous planets)		[planet scope]
#has_modifier_Planet_Wonder_Discovered = yes/no

## Spawns on capital worlds after event chains. 		[planet scope]
#has_modifier_Work_Camps = yes/no
#has_modifier_Galactic_Equality = yes/no
#has_modifier_Augment_Integrated_Systems = yes/no
#has_modifier_Mysterious_Force = yes/no
#has_modifier_Mandatory_Military_Service = yes/no
#has_modifier_Monument_To_The_Stars = yes/no
#has_modifier_Ministery_Of_The_Hunt = yes/no
#has_modifier_Galactic_Outreach_Program = yes/no
#has_modifier_Synopsys_Nodes = yes/no
#has_modifier_Rapid_Assembly_Systems = yes/no
#has_modifier_Combat_Simulator_Systems = yes/no
#has_modifier_Planitary_Defenses = yes/no

## Spawns on capital worlds after event chains. These are timed 		[planet scope]
#has_modifier_Oppressive_Laws = yes/no
#has_modifier_Rights_Movement = yes/no
#has_modifier_Cybernetic_Breaktroughs = yes/no
#has_modifier_Tranquility = yes/no
#has_modifier_Recruitment_Drive = yes/no
#has_modifier_Stargazing = yes/no
#has_modifier_Bounty_Hunting = yes/no
#has_modifier_Diversity_Holiday = yes/no
#has_modifier_Synopsys_Overload = yes/no
#has_modifier_Falling_Behind = yes/no

## Spawns after terraforming		[planet scope]
#has_modifier_Terraform_Result_Better = yes/no
#has_modifier_Terraform_Result_Unbelievable = yes/no
#has_modifier_Terraform_Result_Perfect = yes/no

## Country bonus from discovering the specific modifiers on worlds after surveying		[country scope]
#has_modifier_pm_terraform_speed_one = yes/no
#has_modifier_pm_terraform_speed_two = yes/no
#has_modifier_pm_terraform_speed_three = yes/no
#has_modifier_Precursor_Remnants_Discovery = yes/no
#has_modifier_Precursor_Energy_Grid_Discovery = yes/no
#has_modifier_Precursor_Satellite_Grid_Discovery = yes/no
#has_modifier_Precursor_City_Discovery = yes/no
#has_modifier_Precursor_Shipyards_Discovery = yes/no
#has_modifier_Precursor_Planetary_Gun_Discovery = yes/no
#has_modifier_Precursor_Bunker_Grid_Discovery = yes/no
#has_modifier_Precursor_Mechs_Discovery = yes/no
#has_modifier_Precursor_Planetary_Shield_Discovery = yes/no
#has_modifier_Precursor_Floating_City_Discovery = yes/no
#has_modifier_Precursor_Capital_Complex_Discovery = yes/no
#has_modifier_Precursor_Communication_Hub_Discovery = yes/no
#has_modifier_Precursor_Singularity_Drive_Discovery = yes/no

## Spawns on uninhabitable worlds if specific modifiers were found after surveying		[planet scope]
## allows terraforming of uninhabitable world. "Valuable world" ingame.
#has_modifier_terraforming_candidate_precursor = yes/no

# special precursor modifiers, rare planet modifiers		[planet scope]
#has_modifier_Precursor_Remnants = yes/no
#has_modifier_Precursor_Energy_Grid = yes/no
#has_modifier_Precursor_Satalite_Grid = yes/no
#has_modifier_Precursor_City = yes/no
#has_modifier_Precursor_Shipyards = yes/no
#has_modifier_Precursor_Planetary_Gun = yes/no
#has_modifier_Precursor_Bunker_Grid = yes/no
#has_modifier_Precursor_Mechs = yes/no
#has_modifier_Precursor_Planetary_Shield = yes/no
#has_modifier_Precursor_Floating_City = yes/no
#has_modifier_Precursor_Capital_Complex = yes/no
#has_modifier_Precursor_Communication_Hub = yes/no
#has_modifier_Precursor_Singularity_Drive = yes/no
#has_modifier_Precursor_Eternal_Fortress = yes/no
#################################################