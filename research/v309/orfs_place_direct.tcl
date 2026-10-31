# V309 direct OpenROAD placement, using Nangate45 tech/cell LEF and matched
# mapped Yosys netlists. This bypasses incompatible modern ORFS Python tooling
# in the pinned OpenLane 1.0.2 image; it does NOT claim detailed routing.
set p $::env(V309_PLATFORM_DIR)
set netlist $::env(V309_NETLIST)
set top $::env(V309_TOP)
set out $::env(V309_PLACED_DB)
set die $::env(V309_DIE)
set core $::env(V309_CORE)
read_lef "$p/lef/NangateOpenCellLibrary.tech.lef"
read_lef "$p/lef/NangateOpenCellLibrary.macro.mod.lef"
read_liberty "$p/lib/NangateOpenCellLibrary_typical.lib"
read_verilog $netlist
link_design $top
initialize_floorplan -die_area $die -core_area $core -site FreePDK45_38x28_10R_NP_162NW_34O
make_tracks
place_pins -hor_layers metal5 -ver_layers metal6
global_placement -density 0.65
detailed_placement
write_db $out
puts "V309_PLACED_DB_WRITTEN $out"
