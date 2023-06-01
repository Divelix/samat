import cv2
import numpy as np


class PaintApp:
    def __init__(self, background_image_path: str):
        self.drawing = False
        self.mode = True
        self.brush_size = 5
        self.erase_mode = False
        self.mouse_position = (0, 0)

        # Load the custom background image
        self.background_image = cv2.imread(background_image_path)
        if self.background_image is None:
            raise ValueError("Failed to load the background image")

        # Resize the background image to match the canvas size
        self.background_image = cv2.resize(self.background_image, (500, 500))

        # Create a blank canvas with an alpha channel
        self.canvas = np.zeros((500, 500, 4), dtype=np.uint8)

        cv2.namedWindow("Paint", cv2.WINDOW_GUI_NORMAL)
        cv2.setMouseCallback("Paint", self.draw_shape)

    def draw_shape(self, event, x, y, flags, param):
        if event == cv2.EVENT_RBUTTONDOWN:
            self.drawing = True
            if self.erase_mode:
                cv2.circle(self.canvas, (x, y), self.brush_size, (0, 0, 0, 0), -1)
            else:
                cv2.circle(self.canvas, (x, y), self.brush_size, (0, 0, 255, 127), -1)

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                if self.erase_mode:
                    cv2.circle(self.canvas, (x, y), self.brush_size, (0, 0, 0, 0), -1)
                else:
                    if self.mode:
                        cv2.circle(self.canvas, (x, y), self.brush_size, (0, 0, 255, 127), -1)
                    else:
                        cv2.line(self.canvas, (x, y), (x, y), (0, 255, 0, 127), self.brush_size)

        elif event == cv2.EVENT_RBUTTONUP:
            self.drawing = False
            if self.erase_mode:
                cv2.circle(self.canvas, (x, y), self.brush_size, (0, 0, 0, 0), -1)
            else:
                if self.mode:
                    cv2.circle(self.canvas, (x, y), self.brush_size, (0, 0, 255, 127), -1)
                else:
                    cv2.line(self.canvas, (x, y), (x, y), (0, 255, 0, 127), self.brush_size)

        self.mouse_position = (x, y)

    def run(self):
        while True:
            display = self.background_image.copy()

            # Resize the canvas to match the background image
            canvas_resized = cv2.resize(self.canvas, (self.background_image.shape[1], self.background_image.shape[0]))

            # Apply alpha blending to combine the canvas and the background image
            alpha = canvas_resized[:, :, 3] / 255.0
            alpha = np.expand_dims(alpha, axis=-1)
            blended = cv2.convertScaleAbs(canvas_resized[:, :, :3] * alpha + display[:, :, :3] * (1 - alpha))

            # Update the display with the blended image
            display[:, :, :3] = blended

            x, y = self.mouse_position
            cv2.circle(display, (x, y), self.brush_size, (128, 128, 128, 255), 1)
            cv2.imshow("Paint", display)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("m"):
                self.mode = not self.mode
            elif key == ord("="):
                self.brush_size += 1
            elif key == ord("-"):
                self.brush_size = max(1, self.brush_size - 1)
            elif key == ord("c"):
                self.erase_mode = not self.erase_mode
            elif key == 27:
                break

        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = PaintApp("/home/divelix/Pictures/IMG_20230415_183701.jpg")
    app.run()
