import pygame as pg
import numpy as np
import glob
import cv2
import os
import pygame.camera


class Matrix:
    def __init__(self, app, font_size=7):
        self.move = "video/load.mp4"
        self.clock = pg.time.Clock()
        self.tick_count = 1
        self.app = app
        self.FONT_SIZE = font_size
        self.SIZE = self.ROWS, self.COLS = app.HEIGHT // font_size, app.WIDTH // font_size
        self.katakana = np.array([chr(int('0x30a0', 16) + i) for i in range(96)] + ['' for i in range(10)])
        self.font = pg.font.Font('font/ms mincho.ttf', font_size, bold=True)

        self.matrix = np.random.choice(self.katakana, self.SIZE)
        self.char_intervals = np.random.randint(25, 50, size=self.SIZE)
        self.cols_speed = np.random.randint(1, 500, size=self.SIZE)
        self.prerendered_chars = self.get_prerendered_chars()

        if os.path.exists("video/frame_001.jpg"):
            self.image_list = glob.glob('video/*.jpg')
            self.image_list.sort()
            self.image_list = self.get_image()


    def get_frame_langth(self):
        move = cv2.VideoCapture(self.move)
        return int(move.get(cv2.CAP_PROP_FRAME_COUNT))

    def get_video(self):
        if os.path.exists("video/frame_001.jpg") == False:
            move = cv2.VideoCapture(self.move)
            i = 1
            length = self.get_frame_langth()
            index = len(str(length))
            while i <= length:
                ret, frame = move.read()
                resize_frame = cv2.resize(frame, (960, 720), interpolation=cv2.INTER_AREA)
                gray = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2GRAY)

                cv2.imwrite("video/frame_%s.jpg" % str(i).zfill(index), gray)
                i += 1

            self.image_list = glob.glob('video/*.jpg')
            self.image_list.sort()
            self.image_list = self.get_image()
        return True

    def get_image(self):
        pixel_array = []
        for elem in self.image_list:
            image = pg.image.load(str(elem))
            image = pg.transform.scale(image, self.app.RES)
            pixel_array.append(pg.pixelarray.PixelArray(image))

        return pixel_array

    def get_prerendered_chars(self):
        char_colors = [(0, green, 0) for green in range(256)]
        prerendered_chars = {}
        for char in self.katakana:
            prerendered_char = {(char, color): self.font.render(char, True, color) for color in char_colors}
            prerendered_chars.update(prerendered_char)
        return prerendered_chars

    def run(self):
        if self.get_video():
            frames = pg.time.get_ticks()
            self.change_chars(frames)
            self.shift_column(frames)
            self.draw()

    def shift_column(self, frames):
        num_cols = np.argwhere(frames % self.cols_speed == 0)
        num_cols = num_cols[:, 1]
        num_cols = np.unique(num_cols)
        self.matrix[:, num_cols] = np.roll(self.matrix[:, num_cols], shift=1, axis=0)

    def change_chars(self, frames):
        mask = np.argwhere(frames % self.char_intervals == 0)
        new_chars = np.random.choice(self.katakana, mask.shape[0])
        self.matrix[mask[:, 0], mask[:, 1]] = new_chars

    def draw(self):
        langth = self.get_frame_langth()
        self.tick_count += 1
        for y, row in enumerate(self.matrix):
            for x, char in enumerate(row):
                if char:
                    pos = x * self.FONT_SIZE, y * self.FONT_SIZE

                    if self.tick_count == langth:
                        self.tick_count = 1

                    _, red, green, blue = pg.Color(self.image_list[self.tick_count][pos])
                    if red and green and blue:
                        color = (red + green + blue) // 3
                        color = 220 if 140 < color < 220 else color
                        char = self.prerendered_chars[(char, (0, color, 0))]
                        char.set_alpha(color + 70)
                        self.app.surface.blit(char, pos)
        pg.display.update()



class MatrixVision:
    def __init__(self):
        self.RES = self.WIDTH, self.HEIGHT = 960, 720
        pg.init()
        pygame.display.set_caption('matrix visual')
        self.screen = pg.display.set_mode(self.RES)
        self.surface = pg.Surface(self.RES)
        self.clock = pg.time.Clock()
        self.matrix = Matrix(self)

        # pygame.camera.init()
        # self.cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])
        # self.cam.start()

    def draw(self):
        self.surface.fill(pg.Color('black'))
        self.matrix.run()
        self.screen.blit(self.surface, (0, 0))

    def run(self):
        while True:
            self.draw()
            [exit() for i in pg.event.get() if i.type == pg.QUIT]
            pg.display.flip()
            self.clock.tick(30)


if __name__ == '__main__':
    app = MatrixVision()
    app.run()
