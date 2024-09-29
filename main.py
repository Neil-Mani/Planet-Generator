import tkinter as tk
from tkinter import ttk
import numpy as np
from PIL import Image, ImageTk, ImageDraw
from noise import snoise2
import time

class PlanetGenerator:
    def __init__(self, master):
        self.master = master
        master.title("Pixelated Procedural Planet Generator")

        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.pack()

        self.temp_slider = ttk.Scale(master, from_=-100, to=100, orient="horizontal", length=300)
        self.temp_slider.set(0)
        self.temp_slider.pack(pady=10)

        self.temp_label = ttk.Label(master, text="Temperature: 0°C")
        self.temp_label.pack()

        self.pixel_size_slider = ttk.Scale(master, from_=1, to=20, orient="horizontal", length=300)
        self.pixel_size_slider.set(5)
        self.pixel_size_slider.pack(pady=10)

        self.pixel_size_label = ttk.Label(master, text="Pixel Size: 5")
        self.pixel_size_label.pack()

        self.generate_button = ttk.Button(master, text="Generate New Planet", command=self.generate_new_planet)
        self.generate_button.pack(pady=10)

        self.generation_time_label = ttk.Label(master, text="Generation Time: N/A")
        self.generation_time_label.pack()

        self.planet_image = None
        self.photo = None
        self.seed = np.random.randint(0, 1000000)

        self.generate_new_planet()

    def get_noise(self, nx, ny, octaves=4):
        return snoise2(nx, ny, octaves=octaves, persistence=0.5, lacunarity=2.0, base=self.seed)

    def get_biome_color(self, h, temperature, water_level):
        if temperature > 80:  # Extremely hot planets
            lava_intensity = (temperature - 80) / 20  # 0 to 1 scale for 80°C to 100°C
            if h < water_level:  # Small water bodies or lava lakes
                return (int(210 + lava_intensity * 45), int(100 - lava_intensity * 100), 0)
            else:
                rock_variation = self.get_noise(h * 5, temperature * 0.1, octaves=2)
                r = int(180 + lava_intensity * 75 + rock_variation * 20)
                g = int(90 + rock_variation * 30 - lava_intensity * 60)
                b = int(max(0, 50 + rock_variation * 20 - lava_intensity * 50))
                return (min(255, r), min(255, g), b)
        elif h < water_level:  # Ocean
            depth = (water_level - h) / water_level
            if temperature < -20:  # Frozen ocean
                return (int(200 + depth * 55), int(200 + depth * 55), 255)
            else:
                return (int(0 + depth * 60), int(105 + depth * 150), int(148 + depth * 107))
        elif h < water_level + 0.02:  # Beach
            return (210, 180, 140)
        elif temperature < -20:  # Tundra
            return (250, 250, 250)
        elif temperature < 0:  # Taiga
            return (150, 180, 150)
        elif temperature < 20:  # Temperate forest
            return (34, 139, 34)
        elif temperature < 30:  # Grassland
            return (154, 205, 50)
        elif temperature < 50:  # Savanna
            return (218, 165, 32)
        else:  # Desert
            return (210, 180, 140)

    def create_planet_image(self, temperature, pixel_size):
        width, height = 400, 400
        center = (width // 2, height // 2)
        radius = 195

        # Adjust water level based on temperature
        base_water_level = 0.4
        water_level = max(0.01, min(0.7, base_water_level - temperature / 200))
        
        # Further reduce water for extremely hot temperatures
        if temperature > 80:
            water_level *= max(0, (100 - temperature) / 20)

        # Create a smaller image that will be scaled up for pixelation
        small_size = width // pixel_size
        small_img = Image.new('RGB', (small_size, small_size), (0, 0, 0))
        small_draw = ImageDraw.Draw(small_img)

        for x in range(small_size):
            for y in range(small_size):
                nx = x / small_size - 0.5
                ny = y / small_size - 0.5
                distance = nx*nx + ny*ny
                if distance <= 0.25:  # Normalized radius
                    h = self.get_noise(nx * 3, ny * 3)
                    color = self.get_biome_color(h, temperature, water_level)
                    small_draw.point((x, y), fill=color)

        # Scale up the small image to create pixelation effect
        img = small_img.resize((width, height), Image.NEAREST)

        # Add clouds (reduce for very hot planets)
        if temperature < 80:
            cloud_intensity = max(0, 1 - temperature / 80)
            cloud_img = Image.new('RGBA', (small_size, small_size), (0, 0, 0, 0))
            cloud_draw = ImageDraw.Draw(cloud_img)
            for x in range(small_size):
                for y in range(small_size):
                    nx = x / small_size - 0.5 + self.seed * 0.1
                    ny = y / small_size - 0.5
                    distance = nx*nx + ny*ny
                    if distance <= 0.25:
                        cloud_value = self.get_noise(nx * 5, ny * 5, octaves=8)
                        if cloud_value > 0.1:
                            alpha = int((cloud_value - 0.1) * 1200 * cloud_intensity)
                            cloud_draw.point((x, y), fill=(255, 255, 255, min(alpha, 255)))

            cloud_img = cloud_img.resize((width, height), Image.NEAREST)
            img = Image.alpha_composite(img.convert('RGBA'), cloud_img)

        return img

    def generate_new_planet(self):
        start_time = time.time()
        
        temperature = self.temp_slider.get()
        self.temp_label.config(text=f"Temperature: {temperature:.1f}°C")

        pixel_size = int(self.pixel_size_slider.get())
        self.pixel_size_label.config(text=f"Pixel Size: {pixel_size}")

        self.seed = np.random.randint(0, 1000000)
        self.planet_image = self.create_planet_image(temperature, pixel_size)
        self.photo = ImageTk.PhotoImage(self.planet_image)
        self.canvas.delete("all")
        self.canvas.create_image(200, 200, image=self.photo)

        end_time = time.time()
        generation_time = end_time - start_time
        self.generation_time_label.config(text=f"Generation Time: {generation_time:.3f} seconds")

root = tk.Tk()
planet_gen = PlanetGenerator(root)
root.mainloop()