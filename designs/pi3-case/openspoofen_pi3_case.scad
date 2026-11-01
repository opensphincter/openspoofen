$fn = 64;

include <assets/ghost_logo_layers_generated.scad>;

mode = "display";

board_length = 85;
board_width = 56;
board_clearance = 1.2;

wall = 2.4;
floor_thickness = 2.2;
base_wall_height = 16;
lid_thickness = 3.2;
lid_skirt_depth = 4.2;
lid_clearance = 0.35;

corner_radius = 6;
standoff_height = 3;
standoff_diameter = 6.4;
standoff_hole_diameter = 2.9;

detail_height = 0.45;
case_color = [0.97, 0.97, 0.96];

outer_length = board_length + board_clearance * 2 + wall * 2;
outer_width = board_width + board_clearance * 2 + wall * 2;
base_height = floor_thickness + base_wall_height;


module rounded_box(size, radius) {
  hull() {
    for (x = [radius, size[0] - radius]) {
      for (y = [radius, size[1] - radius]) {
        translate([x, y, 0]) cylinder(h = size[2], r = radius);
      }
    }
  }
}


module shell_cutaway(size, radius, wall_thickness, cavity_height) {
  translate([wall_thickness, wall_thickness, floor_thickness])
    rounded_box(
      [size[0] - wall_thickness * 2, size[1] - wall_thickness * 2, cavity_height],
      max(radius - wall_thickness, 1)
    );
}


module board_standoffs() {
  hole_xs = [3.5, 61.5];
  hole_ys = [3.5, 52.5];
  for (x = hole_xs) {
    for (y = hole_ys) {
      translate([wall + board_clearance + x, wall + board_clearance + y, floor_thickness])
        difference() {
          cylinder(h = standoff_height, d = standoff_diameter);
          translate([0, 0, -0.01]) cylinder(h = standoff_height + 0.02, d = standoff_hole_diameter);
        }
    }
  }
}


module front_io_cutout() {
  translate([-0.01, 6, 5]) cube([wall + 0.04, outer_width - 12, 9.5]);
}


module side_usb_cutout() {
  translate([24, outer_width - wall - 0.01, 4.5]) cube([outer_length - 31, wall + 0.04, 12.5]);
}


module gpio_relief() {
  translate([12, wall - 0.01, 10.5]) cube([44, wall + 0.04, 5.5]);
}


module ventilation_slots() {
  for (slot_x = [18 : 8 : outer_length - 18]) {
    translate([slot_x, 16, base_height - 0.8]) cube([3, outer_width - 32, 1.6]);
  }
}


module ghost_art_position() {
  translate([
    outer_length / 2 - ghost_art_size[0] / 2,
    outer_width / 2 - ghost_art_size[1] / 2,
    0
  ]) children();
}


module ghost_logo_layers() {
  ghost_art_position() generated_ghost_logo_layers(detail_height);
}


module base_case() {
  difference() {
    union() {
      rounded_box([outer_length, outer_width, base_height], corner_radius);
      board_standoffs();
    }
    shell_cutaway([outer_length, outer_width, base_height], corner_radius, wall, base_wall_height + 1);
    front_io_cutout();
    side_usb_cutout();
    gpio_relief();
    ventilation_slots();
  }
}


module lid_shell() {
  skirt_outer_radius = max(corner_radius - wall * 0.5, 1);
  union() {
    rounded_box([outer_length, outer_width, lid_thickness], corner_radius);
    translate([wall + lid_clearance, wall + lid_clearance, -lid_skirt_depth])
      difference() {
        rounded_box(
          [outer_length - (wall + lid_clearance) * 2, outer_width - (wall + lid_clearance) * 2, lid_skirt_depth],
          skirt_outer_radius
        );
        translate([wall, wall, -0.01])
          rounded_box(
            [outer_length - (wall + lid_clearance) * 2 - wall * 2, outer_width - (wall + lid_clearance) * 2 - wall * 2, lid_skirt_depth + 0.02],
            max(skirt_outer_radius - wall, 1)
          );
      }
  }
}


module lid_with_logo() {
  union() {
    color(case_color) lid_shell();
    translate([0, 0, lid_thickness - 0.001]) ghost_logo_layers();
  }
}


module display_assembly() {
  color(case_color) base_case();
  translate([0, 0, base_height]) lid_with_logo();
}


if (mode == "base") {
  base_case();
} else if (mode == "lid") {
  lid_with_logo();
} else {
  display_assembly();
}