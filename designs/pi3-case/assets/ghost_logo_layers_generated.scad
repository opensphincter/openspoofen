ghost_art_size = [35.838, 43.000];

module generated_ghost_logo_layers(detail_height) {
  color([0.05490, 0.03137, 0.05882])
    linear_extrude(height = detail_height) import("C:/openspoofen/designs/pi3-case/assets/ghost_layer_01.svg");
  color([0.70588, 0.05882, 0.19216])
    linear_extrude(height = detail_height) import("C:/openspoofen/designs/pi3-case/assets/ghost_layer_02.svg");
  color([0.83529, 0.87843, 0.90196])
    linear_extrude(height = detail_height) import("C:/openspoofen/designs/pi3-case/assets/ghost_layer_03.svg");
  color([0.55294, 0.76078, 0.19216])
    linear_extrude(height = detail_height) import("C:/openspoofen/designs/pi3-case/assets/ghost_layer_04.svg");
  color([0.37255, 0.55294, 0.16078])
    linear_extrude(height = detail_height) import("C:/openspoofen/designs/pi3-case/assets/ghost_layer_05.svg");
  color([0.85098, 0.20392, 0.34902])
    linear_extrude(height = detail_height) import("C:/openspoofen/designs/pi3-case/assets/ghost_layer_06.svg");
}
