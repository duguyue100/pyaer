"""DVS128 Test.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function

import numpy as np
import vispy
from vispy import app, scene, visuals, gloo
from vispy.util.transforms import ortho

from pyaer.dvs128 import DVS128


device = DVS128()

print ("Device ID:", device.device_id)
if device.device_is_master:
    print ("Device is master.")
else:
    print ("Device is slave.")
print ("Device Serial Number:", device.device_serial_number)
print ("Device String:", device.device_string)
print ("Device USB bus Number:", device.device_usb_bus_number)
print ("Device USB device address:", device.device_usb_device_address)
print ("Device size X:", device.dvs_size_X)
print ("Device size Y:", device.dvs_size_Y)
print ("Logic Version:", device.logic_version)

# load new config
device.set_bias_from_json("./scripts/configs/dvs128_config.json")
print (device.get_bias())

device.start_data_stream()

clip_value = 3
histrange = [(0, v) for v in (128, 128)]

app.use_app("pyside")

W, H = 128, 128
img_array = np.random.uniform(0, 1, (W, H)).astype(np.float32)

data = np.zeros(4, dtype=[('a_position', np.float32, 2),
                          ('a_texcoord', np.float32, 2)])
data['a_position'] = np.array([[0, 0], [W, 0], [0, H], [W, H]])
data['a_texcoord'] = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])

VERT_SHADER = """
// Uniforms
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_antialias;
// Attributes
attribute vec2 a_position;
attribute vec2 a_texcoord;
// Varyings
varying vec2 v_texcoord;
// Main
void main (void)
{
    v_texcoord = a_texcoord;
    gl_Position = u_projection * u_view * u_model * vec4(a_position,0.0,1.0);
}
"""

FRAG_SHADER = """
uniform sampler2D u_texture;
varying vec2 v_texcoord;
void main()
{
    gl_FragColor = texture2D(u_texture, v_texcoord);
    gl_FragColor.a = 1.0;
}
"""


class Canvas(vispy.app.Canvas):
    def __init__(self):
        vispy.app.Canvas.__init__(self, keys='interactive', size=(300, 300))
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.texture = gloo.Texture2D(
            img_array, interpolation="linear")

        self.program['u_texture'] = self.texture
        self.program.bind(gloo.VertexBuffer(data))

        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        self.projection = ortho(0, W, 0, H, -1, 1)
        self.program['u_projection'] = self.projection

        gloo.set_clear_color('white')

        self._timer = app.Timer('auto', connect=self.update, start=True)
        self.show()

    #  @profile
    def on_draw(self, ev):
        gloo.clear(color=True, depth=True)

        (pol_events, num_pol_event,
         special_events, num_special_event) = \
            device.get_event()

        if num_pol_event != 0:
            pol_on = (pol_events[:, 3] == 1)
            pol_off = np.logical_not(pol_on)
            img_on, _, _ = np.histogram2d(
                    pol_events[pol_on, 1], 127-pol_events[pol_on, 2],
                    bins=(128, 128), range=histrange)
            img_off, _, _ = np.histogram2d(
                    pol_events[pol_off, 1], 127-pol_events[pol_off, 2],
                    bins=(128, 128), range=histrange)
            if clip_value is not None:
                integrated_img = np.clip(
                    (img_on-img_off), -clip_value, clip_value)
            else:
                integrated_img = (img_on-img_off)

            img_array = ((integrated_img+clip_value)/float(
                clip_value*2)).astype(np.float32)
        else:
            img_array[...] = np.zeros(
                (128, 128), dtype=np.uint8).astype(np.float32)

        self.texture.set_data(img_array)
        self.program.draw('triangle_strip')

    #  @profile
    def on_resize(self, event):
        width, height = event.physical_size
        gloo.set_viewport(0, 0, width, height)
        self.projection = ortho(0, width, 0, height, -100, 100)
        self.program['u_projection'] = self.projection

        # Compute thje new size of the quad
        r = width / float(height)
        R = W / float(H)
        if r < R:
            w, h = width, width / R
            x, y = 0, int((height - h) / 2)
        else:
            w, h = height * R, height
            x, y = int((width - w) / 2), 0
        data['a_position'] = np.array(
            [[x, y], [x + w, y], [x, y + h], [x + w, y + h]])
        self.program.bind(gloo.VertexBuffer(data))

#  @profile
def run():
    win = Canvas()
    app.run()


run()
