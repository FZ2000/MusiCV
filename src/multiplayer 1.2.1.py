import cv2
import wave
import numpy as np
import pyaudio
import threading
import time
import random
import copy
import math

"""
Citation:
http://opencv-python-tutroals.readthedocs.io/en/latest/
https://people.csail.mit.edu/hubert/pyaudio/docs/
https://www.tutorialspoint.com/python/python_multithreading.html

This is a music game that is controlled by finger gesture. All the computer vision algorithms are from opencv library
"""

red_circle_resized = cv2.resize(cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/red.jpg'), (50, 50))
green_circle_resized = cv2.resize(cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/green.jpg'), (50, 50))
yellow_circle_resized = cv2.resize(cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/yellow.jpg'), (50, 50))


camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FPS, 100)
fgbg_left = cv2.createBackgroundSubtractorMOG2(0, 50)
fgbg_right = cv2.createBackgroundSubtractorMOG2(0, 50)
data = None


# Store the initial value of data,
# which makes it possible for us to restore data to its original value later in the code
def init():
    global data
    data_orig={ "start": False,
                "show_init_page": True,
                "show_song_menu": False,
                "show_main_game": False,
                "music_playing": False,
                "beat_times": None,
                "beat_times_sup":
                      [45.090, 44.937, 44.791, 44.490, 44.191, 44.036, 43.731, 43.545, 43.340, 43.131, 42.832, 42.694,
                       42.384, 42.082, 41.631, 41.189, 40.731, 40.141, 39.525, 39.242, 39.084, 38.784, 38.498, 38.338,
                       37.754, 37.590, 37.310, 37.138, 36.841, 36.689, 36.386, 36.107, 35.947, 35.650, 35.189, 34.744,
                       34.604, 34.446, 34.296, 33.996, 33.713, 33.549, 33.243, 32.965, 32.792, 32.511, 32.345, 32.052,
                       31.896, 31.600, 31.314, 31.150, 30.850, 30.554, 30.404, 29.953, 29.513, 29.050, 28.757, 28.620,
                       28.456, 28.320, 28.157, 28.021, 27.860, 27.271, 27.561, 27.426, 27.259, 27.123, 26.962, 26.820,
                       26.659, 26.358, 26.060, 25.761, 25.609, 25.317, 25.024, 24.865, 24.728, 24.561, 24.415, 24.264,
                       23.965, 23.829, 23.665, 23.527, 23.362, 23.219, 23.086, 22.929, 22.770, 22.632, 22.468, 22.324,
                       22.165, 22.022, 21.869, 21.565, 21.266, 20.965, 20.819, 20.365, 19.992, 19.469, 19.169, 19.040,
                       18.875, 18.735, 18.572, 18.429, 18.272, 18.135, 17.977, 17.836, 17.679, 17.540, 17.374, 17.230,
                       17.073, 16.773, 16.475, 16.179, 16.033, 15.721, 15.434, 15.281, 15.142, 14.980, 14.834, 14.679,
                       14.381, 14.246, 14.080, 13.945, 13.782, 13.636, 13.487, 13.345, 13.186, 13.043, 12.884, 12.742,
                       12.578, 12.439, 12.281, 11.987, 11.536, 11.383, 11.238, 10.943, 10.643, 10.484, 10.183, 9.992,
                       9.794, 9.585, 9.291, 9.140, 8.843, 8.540, 8.086, 7.647, 7.192, 6.478, 6.592, 6.446, 6.142, 5.852,
                       5.694, 5.392, 5.201, 5.000, 4.794, 4.496, 4.355, 4.046, 3.739, 3.265, 2.840, 2.680, 2.388, 2.223,
                       2.081, 1.806, 1.205, 0.905, 0.738, 0.434, 0.163, 0.0],

                "beat_times_faded": (np.arange(0.120, 250, 0.67)[::-1].tolist()),
                "width": 1280,
                "height": 720,
                "color": [(0,255,0), (0,255,255), (0,0,255)],
                "beat_queue": list(),
                "lag": 2.5,
                "score": 0,
                "circles": [green_circle_resized, yellow_circle_resized, red_circle_resized],
                "starting_pos": [(i, 100) for i in range(60, 366, 60)] + [(i, 100) for i in range(913, 1220, 60)],
                "on_screen_count": 0,
                "count": 0,
                "bg_capture": cv2.VideoCapture("/Users/frank/Documents/GitHub/MusiCV/pic/bg.gif"),
                "normal_bg_capture": cv2.VideoCapture("/Users/frank/Documents/GitHub/MusiCV/pic/bg.gif"),
                "logo": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/logo.jpg'),
                "start_button_static": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/start_static.jpg'),
                "start_button_on": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/start_on.jpg'),
                "setting_button_static": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/setting_static.jpg'),
                "setting_button_on": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/setting_on.jpg'),
                "help_button_static": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/help_static.jpg'),
                "help_button_on": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/help_on.jpg'),
                "quit_button_static": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/quit_static.jpg'),
                "quit_button_on": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/quit_on.jpg'),
                "start_button": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/start_static.jpg'),
                "setting_button": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/setting_static.jpg'),
                "help_button": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/help_static.jpg'),
                "quit_button": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/quit_static.jpg'),
                "smoke": cv2.resize(cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/smoke.jpg'), (50, 50)),
                "threshold": 60,
                "show_setting_menu": False,
                "end": False,
                "song_name_sup_static": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/sup_logo.jpg'),
                "song_name_faded_static": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/faded_logo.jpg'),
                "song_name_sup": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/sup_logo.jpg'),
                "song_name_faded": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/faded_logo.jpg'),
                "song_name_sup_on": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/sup_logo_on.jpg'),
                "song_name_faded_on": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/faded_logo_on.jpg'),
                "bgm": "/Users/frank/Documents/GitHub/MusiCV/audio/Super Mario Bros. - Full.wav",
                "pre_process_blur_switch": True,
                "pre_process_blur_algo": "bila",
                "remove_bg_blur_switch": True,
                "remove_bg_blur_algo": "2dco",
                "setting_menu_display": "orig",
                "previous_page_on": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/previous_page_on.jpg'),
                "previous_page_static": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/previous_page_static.jpg'),
                "next_page_on": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/next_page_on.jpg'),
                "next_page_static": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/next_page_static.jpg'),
                "quit_on": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/quit_on, jpg'),
                "quit_static": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/quit_static.jpg'),
                "return_to_m_on": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/return_to_m_on.jpg'),
                'return_to_m_static': cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/return_to_m_static.jpg'),
                "previous_page": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/previous_page_static.jpg'),
                "next_page": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/next_page_static.jpg'),
                "quit": cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/quit_static.jpg'),
                'return_to_m': cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/return_to_m_static.jpg'),
                'help1': cv2.resize(cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/help1.jpg'), (1280, 720)),
                'help2': cv2.resize(cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/help2.jpg'), (1280, 720)),
                'help3': cv2.resize(cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/help3.jpg'), (1280, 720)),
                'help4': cv2.resize(cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/help4.jpg'), (1280, 720)),
                'help5': cv2.resize(cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/help5.jpg'), (1280, 720)),
                'help_curr_page': cv2.resize(cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/help1.jpg'), (1280, 720)),
                'help_curr_page_num': 1,
                'show_help': False,
                'frame_rate': 20,
                'lightning_cap': cv2.VideoCapture('/Users/frank/Documents/GitHub/MusiCV/pic/lightning.gif'),
                'start_time' : -1,
                'multi_player_mode': False,
                'multi': cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/multi_static.jpg'),
                'single': cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/single_static.jpg'),
                'multi_static': cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/multi_static.jpg'),
                'single_static': cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/single_static.jpg'),
                'multi_on': cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/multi_on.jpg'),
                'single_on': cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/single_on.jpg'),
                'show_mode_selection': False,
                "score_second_player": 0,
                "end_music" : False,
                }
    data = data_orig


# This function recaptures the background
def recap_bg():
    global fgbg_left
    global fgbg_right

    fgbg_left = cv2.createBackgroundSubtractorMOG2(0, 50)
    fgbg_right = cv2.createBackgroundSubtractorMOG2(0, 50)


# This function is called before the music thread runs
def init_sound():
    data["sound"] = pyaudio.PyAudio()
    data["music"] = wave.open(data["bgm"], 'rb')
    data["channels"] = data["music"].getnchannels()
    data["sample_width"] = data["music"].getsampwidth()
    data["frame_rate_music"] = data["music"].getframerate()
    data["n_frames"] = data["music"].getnframes()


# I used many gif file in this program. This enables us to play a gif file repeatedly
def repeat(cap_name, file):
    data[cap_name].release()
    data[cap_name] = cv2.VideoCapture(file)
    _, window = data[cap_name].read()
    return window


# Since opencv don't have functions that allow me to create button-like objects. I programed this function
# To handle the mouse activity
def over_button(event,x,y,flags,param):
    if (x in range(data["width"]//2-len(data["start_button"][0])//2,
                   data["width"]//2+len(data["start_button"][0])//2)
            and y in range(295, 295+len(data["start_button"]))
            and data["show_init_page"] is True):
        data["start_button"] = data["start_button_on"]
        if event == cv2.EVENT_LBUTTONDOWN:
            data["show_init_page"] = False
            data["show_song_menu"] = True
    elif (x in range(data["width"]//2-len(data["setting_button"][0])//2,
                     data["width"]//2+len(data["setting_button"][0])//2)
            and y in range(370, 370+len(data["setting_button"]))
            and data["show_init_page"] is True):
        data["setting_button"] = data["setting_button_on"]
        if event == cv2.EVENT_LBUTTONDOWN:
            data["show_init_page"] = False
            data["show_setting_menu"] = True
    elif (x in range(data["width"]//2-len(data["help_button"][0])//2,
                     data["width"]//2+len(data["help_button"][0])//2)
            and y in range(444, 444+len(data["help_button"]))
            and data["show_init_page"] is True):
        data["help_button"] = data["help_button_on"]
        if event == cv2.EVENT_LBUTTONDOWN:
            data["show_init_page"] = False
            data["show_help"] = True
    elif (x in range(data["width"]//2-len(data["quit_button"][0])//2,
                     data["width"]//2+len(data["quit_button"][0])//2)
            and y in range(518, 518+len(data["quit_button"]))
            and data["show_init_page"] is True):
        data["quit_button"] = data["quit_button_on"]
        if event == cv2.EVENT_LBUTTONDOWN:
            camera.release()
            cv2.destroyAllWindows()
            data["end"] = True
    elif (x in range(data["width"]//2-len(data["song_name_sup"][0])//2,
                     data["width"]//2+len(data["song_name_sup"][0])//2)
            and y in range(241, 241+len(data["song_name_sup"]))
            and data["show_song_menu"] is True):
        data["song_name_sup"] = data["song_name_sup_on"]
        if event == cv2.EVENT_LBUTTONDOWN:
            data["show_song_menu"] = False
            data["show_mode_selection"] = True
            data["show_main_game"] = True
            data["bgm"] = "/Users/frank/Documents/GitHub/MusiCV/audio/Super Mario Bros. - Full.wav"
            data["beat_times"] = data["beat_times_sup"]
    elif (x in range(data["width"]//2-len(data["song_name_faded"][0])//2,
                     data["width"]//2+len(data["song_name_faded"][0])//2)
            and y in range(508, 508+len(data["song_name_faded"]))
            and data["show_song_menu"] is True):
        data["song_name_faded"] = data["song_name_faded_on"]
        if event == cv2.EVENT_LBUTTONDOWN:
            data["show_song_menu"] = False
            data["show_mode_selection"] = True
            data["beat_times"] = data["beat_times_faded"]
            data["bgm"] = "/Users/frank/Documents/GitHub/MusiCV/audio/Faded-2.wav"
    elif (x in range(data["width"] - len(data["next_page"][0]), data["width"])
          and y in range(data["height"]-len(data["next_page"]), data["height"])
          and data["show_help"] is True
          and data["help_curr_page_num"] in range(1, 5)):
        data["next_page"] = data["next_page_on"]
        if event == cv2.EVENT_LBUTTONDOWN:
            data["help_curr_page_num"] += 1
            data["help_curr_page"] = data["help" + str(data["help_curr_page_num"])]
    elif (x in range(0, len(data["previous_page"][0]))
          and y in range(data["height"] - len(data["previous_page"]), data["height"])
          and data["show_help"] is True
          and data["help_curr_page_num"] in range(2, 6)):
        data["previous_page"] = data["previous_page_on"]
        if event == cv2.EVENT_LBUTTONDOWN:
            data["help_curr_page_num"] -= 1
            data["help_curr_page"] = data["help" + str(data["help_curr_page_num"])]
    elif (x in range(data["width"] - len(data["return_to_m"][0]), data["width"])
          and y in range(data["height"]-len(data["return_to_m"]), data["height"])
          and data["show_help"] is True
          and data["help_curr_page_num"] == 5):
        data["return_to_m"] = data["return_to_m_on"]
        if event == cv2.EVENT_LBUTTONDOWN:
            data['show_help'] = False
            data["show_init_page"] = True
            data['help_curr_page_num'] = 1
            data['help_curr_page'] = data['help1']
    elif (x in range(data["width"]//2-len(data["multi"][0])//2,
                     data["width"]//2+len(data["multi"][0])//2)
            and y in range(508, 508+len(data["multi"]))
            and data["show_mode_selection"] is True):
        data["multi"] = data["multi_on"]
        if event == cv2.EVENT_LBUTTONDOWN:
            data["multi_player_mode"] = True
            data["show_mode_selection"] = False
            data["show_main_game"] = True
    elif (x in range(data["width"]//2-len(data["single"][0])//2,
                     data["width"]//2+len(data["single"][0])//2)
            and y in range(241, 241+len(data["single"]))
            and data["show_mode_selection"] is True):
        data["single"] = data["single_on"]
        if event == cv2.EVENT_LBUTTONDOWN:
            data["multi_player_mode"] = False
            data["show_mode_selection"] = False
            data["show_main_game"] = True
    else:
        data["start_button"] = data["start_button_static"]
        data["setting_button"] = data["setting_button_static"]
        data["help_button"] = data["help_button_static"]
        data["quit_button"] = data["quit_button_static"]
        data["song_name_sup"] = data["song_name_sup_static"]
        data["song_name_faded"] = data["song_name_faded_static"]
        data["next_page"] = data["next_page_static"]
        data["previous_page"] = data["previous_page_static"]
        data['return_to_m'] = data['return_to_m_static']
        data['multi'] = data['multi_static']
        data['single'] = data['single_static']


# This creates the song menu
def get_song_menu():
    _, window = data["bg_capture"].read()
    if window is None:
        window = repeat("bg_capture", '/Users/frank/Documents/GitHub/MusiCV/pic/bg.gif')
    overlay(window, data["song_name_sup"], 241, data["width"]//2-len(data["song_name_sup"][0])//2)
    overlay(window, data["song_name_faded"], 508, data["width"] // 2 - len(data["song_name_faded"][0]) // 2)
    return window


# This creates the main menu
def get_starting_window():

    _, window = data["bg_capture"].read()

    if window is None:
        window = repeat("bg_capture", '/Users/frank/Documents/GitHub/MusiCV/pic/bg.gif')

    logo = cv2.imread('/Users/frank/Documents/GitHub/MusiCV/pic/logo.jpg')
    window[176:295, 402:878] = logo
    overlay(window, data["start_button"], 295, data["width"]//2-len(data["start_button"][0])//2)
    overlay(window, data["setting_button"], 370, data["width"]//2-len(data["setting_button"][0])//2)
    overlay(window, data["help_button"], 444, data["width"]//2-len(data["help_button"][0])//2)
    overlay(window, data["quit_button"], 518, data["width"]//2-len(data["quit_button"][0])//2)

    return window


# Thhis creates help and tips
def get_help_window():
    window = copy.deepcopy(data["help_curr_page"])
    if data["help_curr_page_num"] in range(1, 5):
        overlay(window, data["next_page"], data["height"]-len(data["next_page"]-5),
                data["width"]- len(data["next_page"][0])-5)
    if data["help_curr_page_num"] in range(2, 6):
        overlay(window, data["previous_page"], data["height"] - len(data["previous_page"]), 0)
    if data["help_curr_page_num"] == 5:
        overlay(window, data["return_to_m"], data["height"]-len(data["return_to_m"]),
                data["width"]-len(data["return_to_m"][0]))
    return window


# This creates the window in which player chooses between multiplayer and single player
def get_mode_window():
    _, window = data["bg_capture"].read()

    if window is None:
        window = repeat("bg_capture", '/Users/frank/Documents/GitHub/MusiCV/pic/bg.gif')

    overlay(window, data["single"], 241, data["width"] // 2 - len(data["single"][0]) // 2)
    overlay(window, data["multi"], 508, data["width"] // 2 - len(data["multi"][0]) // 2)

    return window


# This function overlays a graph on another
def overlay(target, obj, start_row_index, start_col_index):
    for row in range(len(obj)):
        for col in range(len(obj[0])):
            target[row+start_row_index][col+start_col_index] = obj[row][col]


# Beat object. The circle that is draw on the main game canvas
class beat:
    def __init__(self, time_start, time_end, pos):
        self.time_start = time_start
        self.time_end = time_end
        self.pos = pos
        self.deactivate = False

    def get_time_end(self):
        return self.time_end

    def get_time_start(self):
        return self.time_start

    def get_pos(self):
        return self.pos

    def __repr__(self):
        if self.deactivate:
            status = "deactivated"
        else:
            status = "activated"

        return("A %s beat at (%d, %d) that starts at %d and ends at %d" %(status,
                                                                          self.pos[0],
                                                                          self.pos[1],
                                                                          self.time_start,
                                                                          self.time_end))


# This is the function that the music thread calls
def play_music():
    time.sleep(data["lag"])
    stream = data["sound"].open(format=data["sound"].get_format_from_width(data["sample_width"]),
                                channels=data["channels"],
                                rate=data["frame_rate_music"],
                                output=True)
    mus_data = data["music"].readframes(1024)
    while not data["end_music"]:
        stream.write(mus_data)
        mus_data = data["music"].readframes(1024)
    return 11111


# Get frame from the camera
def get_frame():
    ret, f = camera.read()
    if data["pre_process_blur_switch"] is True:
        if data["pre_process_blur_algo"] == "bila":
            f = cv2.bilateralFilter(f, 5, 1000, 1000)
        if data["pre_process_blur_algo"] == "2dco":
            kernel = np.ones((5, 5), np.uint8) / 25
            f = cv2.filter2D(f, -1, kernel)
        if data["pre_process_blur_algo"] == "aver":
            f = cv2.blur(f, (5,5))
        if data["pre_process_blur_algo"] == "gaus":
            f = cv2.GaussianBlur(f, (5, 5), 0)
        if data["pre_process_blur_algo"] == "medi":
            f = cv2.medianBlur(f, 5)
    f = cv2.flip(f, 1)
    return f


# Find the max contours
def get_max_contour(contours):
    max_contour_area = 0
    max_contour = None
    for contour in contours:
        curr_area = cv2.contourArea(contour)
        if max_contour is None or curr_area > max_contour_area:
            max_contour_area = curr_area
            max_contour = contour
    return max_contour


# Get the region where the computer will check fingers
# Take in frame and a string(Left or Right) as the input
def get_search_region(f, s):
    bounds = get_search_region_bound(f, s)
    return f[bounds[0]:bounds[1], bounds[2]:bounds[3]]


# We slice the middle one third of the screen out because we don't want players' face messing everything up.
# This returns the bounds of left search region and right search region
def get_search_region_bound(f, s):
    frame_height = len(f)
    frame_width = len(f[0])
    if s == 'left':
        left_up_bound = 0
        left_right_bound = int(1 / 3 * frame_width)
        result = (left_up_bound, frame_height, 0, left_right_bound)
        return result
    if s == 'right':
        right_up_bound = 0
        right_left_bound = int(2 / 3 * frame_width)
        result = (right_up_bound, frame_height, right_left_bound, frame_width)
        return result


# This function remove the background of the input taken by the webcam. Generally, it uses a background subtraction
# algorithm, which regards all static objects as part of the background
def remove_bg(search_region, s):
        # Create mask
        mask = None
        if s == "left":
            mask = fgbg_left.apply(search_region, learningRate=0)
        if s == "right":
            mask = fgbg_right.apply(search_region, learningRate=0)
        if data["remove_bg_blur_switch"] is True:
            if data["pre_process_blur_algo"] == "bila":
                mask = cv2.bilateralFilter(mask, 5, 100, 100)
            elif data["pre_process_blur_algo"] == "2dco":
                kernel = np.ones((5, 5), np.uint8) / 25
                mask = cv2.filter2D(mask, -1, kernel)
            elif data["pre_process_blur_algo"] == "aver":
                mask = cv2.blur(mask, (5, 5))
            elif data["pre_process_blur_algo"] == "gaus":
                mask = cv2.GaussianBlur(mask, (5, 5), 0)
            elif data["pre_process_blur_algo"] == "medi":
                mask = cv2.medianBlur(mask, 5)
        # Apply mask
        finger = cv2.bitwise_and(search_region, search_region, mask=mask)
        return finger


# This function smooth the edge of the output
def edge_smooth(finger):
    finger_blur = cv2.bilateralFilter(finger, 5, 1000, 1000)
    _, thresh = cv2.threshold(finger_blur, data['threshold'], 255, cv2.THRESH_BINARY)
    finger_gray = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
    return finger_gray


# This function finds the highest point in the contour
def get_finger_tip(finger):
    finger_tip = None
    finger_tip_y = float('inf')
    if finger is not None:
        for point in finger:
            point = tuple(point[0])
            if point[1] < finger_tip_y:
                finger_tip = point
                finger_tip_y = point[1]
    return finger_tip


# This function returns the position of the finger
def get_finger_pos(f):
    # Set up the search region
    left_search_region = get_search_region(f, 'left')
    right_search_region = get_search_region(f, 'right')

    # Get rid of the BG in the search region
    left = remove_bg(left_search_region, "left")
    right = remove_bg(right_search_region, "right")

    # # Smooth the edge
    finger_left = edge_smooth(left)
    finger_right = edge_smooth(right)

    # # Find contour
    _, contours_left, _ = cv2.findContours(finger_left, cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
    _, contours_right, _ = cv2.findContours(finger_right, cv2.RETR_TREE,
                                            cv2.CHAIN_APPROX_SIMPLE)

    # Spot finger among contours
    finger_left = get_max_contour(contours_left)
    finger_right = get_max_contour(contours_right)

    left_finger_tip = None
    right_finger_tip = None

    if finger_left is not None:
        # Find finger tip
        left_finger_tip = get_finger_tip(finger_left)
        # Print finger tip

    if finger_right is not None:
        right_finger_tip = get_finger_tip(finger_right)
        right_finger_tip = (int(right_finger_tip[0]+len(f[0])*0.66),
                            right_finger_tip[1])

    return left_finger_tip, right_finger_tip


# This shows the position of the finger tip on the left search region
def draw_left_search_region(window, left_search_region):
    real_size = (int(len(window[0])/6), int(len(window)/2))

    resized = cv2.resize(left_search_region, real_size)
    window[:int(len(window)/2),
           int(len(window[0])/3):int(len(window[0])/2)-1] = resized

# This shows the position of the finger tip on the right search region
def draw_right_search_region(window, right_search_region):
    real_size = (int(len(window[0])/6), int(len(window)/2))

    resized = cv2.resize(right_search_region, real_size)
    window[:int(len(window)/2),
           int(len(window[0])/2):int(len(window[0])/3*2)] = resized


# Choose the starting position of a beat randomly
def get_new_pos():
    return random.choice(list(data["starting_pos"]))


# Determines if a beat should be drawed on the screen
def should_draw(curr_time, beat_time):
    return abs(curr_time-beat_time) <= 0.45


# This function updates the beats that should be drawed on the screen and but it into a list
def update_beats_queue(t):
    while len(data["beat_times"]) != 0:
            next_beat = data["beat_times"].pop()
            if should_draw(t, next_beat):
                new_beat_pos = get_new_pos()
                new_beat = beat(next_beat, next_beat+data["lag"],
                                new_beat_pos)
                data["beat_queue"].append(new_beat)
            else:
                data["beat_times"].append(next_beat)
                break


# For each frame, this function is called to update the position of all the beats
def update_beats_position(t):
        for beat in data["beat_queue"]:
                    beat.pos = [beat.pos[0], beat.pos[1] + 13]


# This draw the play zone, which is the zone in which all the main gamming elements are
def draw_play_zone(window, t):
    update_beats_position(t)
    update_beats_queue(t)
    for beat in data["beat_queue"]:
        if not np.array_equal(beat, data["smoke"]):
            if beat.get_time_end() >= t:
                remain = int(beat.get_time_end() - t)
                cx, cy = beat.get_pos()
                if beat.deactivate:
                    window[cy - 25:cy + 25, cx - 25:cx + 25] = data["smoke"]
                else:
                    img = data["circles"][remain]
                    window[cy-25:cy+25, cx-25:cx+25] = img


# This function displays score(s) on the screen
def display_score(window):
    if data["multi_player_mode"] is False:
        text = ("Score %d" % (data["score"]))
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(window, text, (585, 400), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    else:
        text_des1 = "Player 1:"
        text_player1 = ("Score %d" % (data["score"]))
        text_des2 = "Player 2:"
        text_player2 = ("Score %d" % (data["score_second_player"]))
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.line(window, (640, 0), (640, 800), (0,0,255), 5)
        cv2.putText(window, text_des1, (480, 400), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(window, text_player1, (480, 450), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(window, text_des2, (660, 400), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(window, text_player2, (660, 450), font, 1, (255, 255, 255), 2, cv2.LINE_AA)


# This function determines if a finger points inside a beat
def within(beat_pos, left_finger, right_finger):
    return ((math.sqrt((left_finger[0]-beat_pos[0])**2
                  +(left_finger[1]-beat_pos[1])**2) <= 45) or
            (math.sqrt((right_finger[0] - beat_pos[0]) ** 2
                  +(right_finger[1] - beat_pos[1]) ** 2) <= 45))


# This function determines if a beat is on the left or right
def is_in_zone_one(pos):
    return pos[0] <= 426


# this function updates the score
def count_point(data, left_finger, right_finger, t):
    if data["multi_player_mode"] is False:
        for index in range(len(data["beat_queue"])):
            beat = data["beat_queue"][index]
            if not np.array_equal(beat, data["smoke"]):
                beat_pos = beat.get_pos()
                if within(beat_pos, left_finger, right_finger) and not beat.deactivate:
                    if (beat.get_time_end() - t) <= 0.1:
                        data["score"] += 2
                        beat.deactivate = True
                    elif (beat.get_time_end() - t) <= 0.2:
                        data["score"] += 1
                        beat.deactivate = True
    else:
        for index in range(len(data["beat_queue"])):
            beat = data["beat_queue"][index]
            if not np.array_equal(beat, data["smoke"]):
                beat_pos = beat.get_pos()
                if within(beat_pos, left_finger, right_finger) and not beat.deactivate:
                    if (beat.get_time_end() - t) <= 0.1:
                        if is_in_zone_one(beat_pos):
                            data["score"] += 2
                        else:
                            data["score_second_player"] += 1
                        beat.deactivate = True
                    elif (beat.get_time_end() - t) <= 0.2:
                        if is_in_zone_one(beat_pos):
                            data["score"] += 1
                        else:
                            data["score_second_player"] += 1
                        beat.deactivate = True


# This function is called when threshold is changed in the setting menu
def update_threshold(val):
    data["threshold"] = val


# This function is called when the player swich on or off the blurring filter #1
def update_pre_process_blur_switch(val):
    if val == 1:
        data["pre_process_blur_switch"] = True
    else:
        data["pre_process_blur_switch"] = False


# This function is called when the player change the blurring algorithm #1
def update_pre_process_blur_algo(val):
    if val == 0:
        data["pre_process_blur_algo"] = "bila"
    elif val == 1:
        data["pre_process_blur_algo"] = "2dco"
    elif val == 2:
        data["pre_process_blur_algo"] = "aver"
    elif val == 3:
        data["pre_process_blur_algo"] = "gaus"
    elif val == 4:
        data["pre_process_blur_algo"] = "medi"


# This function is called when the player swich on or off the blurring filter #2
def update_remove_bg_blur_switch(val):
    if val == 1:
        data["remove_bg_blur_switch"] = True
    else:
        data["remove_bg_blur_switch"] = False


# This function is called when the player change the blurring algorithm #2
def update_remove_bg_blur_algo(val):
    if val == 0:
        data["remove_bg_blur_algo"] = "bila"
    elif val == 1:
        data["remove_bg_blur_algo"] = "2dco"
    elif val == 2:
        data["remove_bg_blur_algo"] = "aver"
    elif val == 3:
        data["remove_bg_blur_algo"] = "gaus"
    elif val == 4:
        data["remove_bg_blur_algo"] = "medi"


# This updates the output in the setting menu
def update_setting_display(val):
    if val == 0:
        data["setting_menu_display"] = "orig"
    elif val == 1:
        data["setting_menu_display"] = "nobg"
    elif val == 2:
        data["setting_menu_display"] = "cont1"
    elif val == 3:
        data["setting_menu_display"] = "cont2"


# This displays the frame rate in the setting menu
def get_frame_rate_display():
    window = np.zeros((100, 100, 3))
    cv2.putText(window, ("fps:" + str(data["frame_rate"])),
                (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255), 2,cv2.LINE_AA)
    return window


# This is the main game. In general, this is where every activity is happened
def main_game(music):
    init()
    while 1:
        start = time.time()
        if data["end"] is True:
            key = cv2.waitKey(1)
            camera.release()
            cv2.destroyAllWindows()
            break
        elif data['show_init_page'] is True:
            key = cv2.waitKey(1)
            window = get_starting_window()
        elif data["show_setting_menu"] is True:
            key = cv2.waitKey(1)
            cv2.namedWindow("Setting")
            cv2.resizeWindow('image', 800, 800)

            cv2.createTrackbar("Threshold", "Setting", 60, 255, update_threshold)

            switch1 = "Blurring in preprocessing stage: 0->Off 1->On"
            cv2.createTrackbar(switch1, "Setting", 1, 1, update_pre_process_blur_switch)

            switch2 = "Blurring algorithm in preprocessing stage: " \
                      "\n 0->Bilateral Filtering \n1-->2D Convolution" \
                      "\n 2->Averaging \n3->Gaussian 4->Median"
            cv2.createTrackbar(switch2, "Setting", 0, 4, update_pre_process_blur_algo)

            switch3 = "Blurring after the background is removed: 0->Off 1->On"
            cv2.createTrackbar(switch3, "Setting", 1, 1, update_remove_bg_blur_switch)

            switch4 = "Blurring algorithm after the background is removed: " \
                      "\n 0->Bilateral Filtering \n1-->2D Convolution" \
                      "\n 2->Averaging \n3->Gaussian 4->Median"
            cv2.createTrackbar(switch4, "Setting", 0, 4, update_pre_process_blur_algo)

            switch5 = "Output type: " \
                      "\n 0->Original \n1-->No background" \
                      "\n 2->Contour1 \n3->Contour1"
            cv2.createTrackbar(switch5, "Setting", 0, 3, update_setting_display)

            frame = get_frame()
            left_search_region = get_search_region(frame, 'left')
            right_search_region = get_search_region(frame, 'right')
            left_nobg = remove_bg(left_search_region, "left")
            right_nobg = remove_bg(right_search_region, "right")
            finger_left = edge_smooth(left_nobg)
            finger_right = edge_smooth(right_nobg)
            _, contours_left, _ = cv2.findContours(finger_left, cv2.RETR_TREE,
                                                   cv2.CHAIN_APPROX_SIMPLE)
            _, contours_right, _ = cv2.findContours(finger_right, cv2.RETR_TREE,
                                                    cv2.CHAIN_APPROX_SIMPLE)
            finger_left_contour = get_max_contour(contours_left)
            finger_right_contour = get_max_contour(contours_right)

            left_finger_tip = None
            right_finger_tip = None

            if finger_left is not None:
                # Find finger tip
                left_finger_tip = get_finger_tip(finger_left_contour)

            if finger_right is not None:
                right_finger_tip = get_finger_tip(finger_right_contour)

            if data["setting_menu_display"] == "orig":
                left_img = left_search_region
                right_img = right_search_region
            elif data["setting_menu_display"] == "nobg":
                left_img = left_nobg
                right_img = right_nobg
            elif data["setting_menu_display"] == "cont1":
                left_img = left_nobg
                right_img = right_nobg
                cv2.drawContours(left_img, finger_left_contour, -1, (0, 255, 0), 3)
                cv2.drawContours(right_img, finger_right_contour, -1, (0, 255, 0), 3)
            elif data["setting_menu_display"] == "cont2":
                left_img = left_search_region
                right_img = right_search_region
                cv2.drawContours(left_img, finger_left_contour, -1, (0, 255, 0), 3)
                cv2.drawContours(right_img, finger_right_contour, -1, (0, 255, 0), 3)
            if left_finger_tip is not None:
                cv2.circle(left_img, left_finger_tip, 30, color=(255, 0, 0), thickness=5)
            if right_finger_tip is not None:
                cv2.circle(right_img, right_finger_tip, 30, color=(0, 255, 0), thickness=5)

            both_finger = np.concatenate((left_img, right_img), axis=1)
            fr = get_frame_rate_display()
            cv2.imshow('Setting', fr)
            cv2.imshow("Finger Output", both_finger)
            cv2.moveWindow("Finger Output", 40, 30)
            key = cv2.waitKey(1)
            if key == ord("r"):
                recap_bg()
            if key == 27:
                cv2.destroyWindow("Finger Output")
                cv2.destroyWindow("Setting")
                data["show_setting_menu"] = False
                data['show_init_page'] = True
        elif data['show_help'] is True:
            window = get_help_window()
            key = cv2.waitKey(1)
        elif data['show_song_menu'] is True:
            window = get_song_menu()
            key = cv2.waitKey(1)
            if key == ord("q"):
                data["show_init_page"] = True
                data["show_main_game"] = False
        elif data['show_mode_selection'] is True:
            window = get_mode_window()
            key = cv2.waitKey(1)
            if key == ord("q"):
                data["show_init_page"] = True
                data["show_main_game"] = False
        elif data["show_main_game"] is True:
            # Set up the search region
            frame = get_frame()

            # Get the position of the fingers and draw them on the frame
            left_finger, right_finger= get_finger_pos(frame)

            cv2.circle(frame, left_finger, 30, color=(255, 0, 0), thickness=5)
            cv2.circle(frame, right_finger, 30, color=(255, 0, 0), thickness=5)

            # Get two search region
            left_search_region = get_search_region(frame, 'left')
            right_search_region = get_search_region(frame, 'right')

            # Set up the window(canvas), which will be white at first

            curr_time = time.time()
            time_elapse = curr_time - data["start_time"]

            data["bg_capture"] = data["normal_bg_capture"]

            if int(time_elapse) in range(53, 97):
                data["bg_capture"] = data["lightning_cap"]

            ret, window = data["bg_capture"].read()

            if window is None:
                data["bg_capture"].release()
                data["lightning_cap"] = cv2.VideoCapture("/Users/frank/Documents/GitHub/MusiCV/pic/lightning.gif")
                data["normal_bg_capture"] = cv2.VideoCapture("/Users/frank/Documents/GitHub/MusiCV/pic/bg.gif")
                if int(time_elapse) in range(55, 97):
                    data["bg_capture"] = data["lightning_cap"]
                else:
                    data["bg_capture"] = data["normal_bg_capture"]

                _, window = data["bg_capture"].read()

            window = cv2.resize(window, (1280, 720))

            # If the player choose the start the game, the music will start playing
            if data["start"]:
                # Draw play zone on the window
                draw_play_zone(window, time_elapse)
                if not data["music_playing"]:
                    init_sound()
                    data["music_playing"] = True
                    music.start()
                    # Display Score
                if left_finger is not None and right_finger is not None:
                    count_point(data, left_finger, right_finger, time_elapse)
                display_score(window)

            # Draw the search region on the window
            draw_left_search_region(window, left_search_region)
            draw_right_search_region(window, right_search_region)

            # Mark where the player is pointing
            cv2.circle(window, left_finger, 30, color=(255,0,0), thickness=5)
            cv2.circle(window, right_finger, 30, color=(0, 255, 0), thickness=5)

            # Show the window
            cv2.line(window, (0, 485), (1280, 485), (255, 255, 255), 10)
            key = cv2.waitKey(1)
            # Start

            if key == ord("s"):
                data["start"] = True
                data["start_time"] = time.time()

            # Quit
            elif key == ord("q"):
                data["show_init_page"] = True
                data["show_main_game"] = False
                data["end_music"] = True
                data['start'] = False
                init()
                music = threading.Thread(target=play_music)
            elif key == ord("r"):
                recap_bg()
        end = time.time()
        data["frame_rate"] = int(1/(end-start))
        cv2.imshow("musicCV", window)
        cv2.moveWindow("musicCV", 40, 30)
        cv2.setMouseCallback('musicCV', over_button)


def main():
    thread1 = threading.Thread(target=play_music)
    main_game(thread1)


if __name__ == "__main__":
    main()

