import requests
import customtkinter as ctk
from PIL import Image, ImageTk
from datetime import datetime
import time

# Configuration
API_KEY = "1893a50ceeb82342cb7155224a6d10ed"

class VertexWeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Vertex Pro Weather Dashboard")
        self.geometry("500x700")
        
        # Background Dictionary
        self.bg_images = {
            "Clear": "https://images.unsplash.com/photo-1506466010722-395aa2bef877?q=80&w=1000",
            "Clouds": "https://images.unsplash.com/photo-1501630834273-4b5604d2ee31?q=80&w=1000",
            "Rain": "https://images.unsplash.com/photo-1438449805896-28a666819a20?q=80&w=1000",
            "Haze": "https://images.unsplash.com/photo-1485236715598-c88513054974?q=80&w=1000",
            "Snow": "https://images.unsplash.com/photo-1491002052546-bf38f186af56?q=80&w=1000",
            "Default": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=1000"
        }

        # Background Label
        self.bg_label = ctk.CTkLabel(self, text="")
        self.bg_label.place(relx=0.5, rely=0.5, anchor="center")

        # Fixed Frame (No RGBA error now)
        self.main_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=20, border_width=2, border_color="#333333")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.9)

        # 1. Date & Time
        self.time_label = ctk.CTkLabel(self.main_frame, text="", font=("Arial", 35, "bold"), text_color="#00d2ff")
        self.time_label.pack(pady=(20, 0))
        self.date_label = ctk.CTkLabel(self.main_frame, text="", font=("Arial", 14), text_color="#bdc3c7")
        self.date_label.pack()

        # 2. Search
        self.entry = ctk.CTkEntry(self.main_frame, placeholder_text="Enter City (e.g. Delhi)", width=220, height=40)
        self.entry.pack(pady=20)
        self.search_btn = ctk.CTkButton(self.main_frame, text="Update Dashboard", command=self.fetch_all, fg_color="#3498db", hover_color="#2980b9")
        self.search_btn.pack()

        # 3. Weather Details
        self.city_display = ctk.CTkLabel(self.main_frame, text="Ready to Search", font=("Arial", 22, "bold"), text_color="white")
        self.city_display.pack(pady=(25, 5))
        
        self.temp_display = ctk.CTkLabel(self.main_frame, text="--°C", font=("Arial", 65, "bold"), text_color="#ffffff")
        self.temp_display.pack()

        self.desc_display = ctk.CTkLabel(self.main_frame, text="Enter city for details", font=("Arial", 16, "italic"), text_color="#ecf0f1")
        self.desc_display.pack()

        # 4. Humidity/Wind
        self.extra_info = ctk.CTkLabel(self.main_frame, text="Humidity: -- | Wind: --", font=("Arial", 13), text_color="#bdc3c7")
        self.extra_info.pack(pady=15)

        # 5. AQI Box
        self.aqi_val = ctk.CTkLabel(self.main_frame, text="AQI: --", font=("Arial", 18, "bold"), text_color="#95a5a6")
        self.aqi_val.pack(pady=10)

        self.update_clock()

    def update_clock(self):
        now = datetime.now()
        self.time_label.configure(text=now.strftime("%H:%M:%S"))
        self.date_label.configure(text=now.strftime("%A, %d %B %Y"))
        self.after(1000, self.update_clock)

    def update_bg(self, condition):
        img_url = self.bg_images.get(condition, self.bg_images["Default"])
        try:
            raw_data = requests.get(img_url, stream=True).raw
            img = Image.open(raw_data).resize((500, 700))
            bg_img = ImageTk.PhotoImage(img)
            self.bg_label.configure(image=bg_img)
            self.bg_label.image = bg_img 
        except: pass

    def fetch_all(self):
        city = self.entry.get()
        if not city: return
        
        try:
            w_res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}").json()
            if w_res.get("cod") == 200:
                main_weather = w_res['weather'][0]['main']
                self.city_display.configure(text=f"{w_res['name']}, {w_res['sys']['country']}")
                self.temp_display.configure(text=f"{round(w_res['main']['temp'])}°C")
                self.desc_display.configure(text=main_weather)
                self.extra_info.configure(text=f"Humidity: {w_res['main']['humidity']}% | Wind: {round(w_res['wind']['speed']*3.6)} km/h")
                self.update_bg(main_weather)
                self.fetch_aqi(w_res['coord']['lat'], w_res['coord']['lon'])
            else:
                self.city_display.configure(text="City Not Found!")
        except:
            self.city_display.configure(text="Network Error!")

    def fetch_aqi(self, lat, lon):
        a_res = requests.get(f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}").json()
        aqi = a_res['list'][0]['main']['aqi']
        pm25 = a_res['list'][0]['components']['pm2_5']
        levels = ["", "Good", "Fair", "Moderate", "Poor", "Very Poor"]
        color = "#00FF88" if aqi <= 2 else ("#FFCC00" if aqi == 3 else "#FF4D4D")
        self.aqi_val.configure(text=f"AQI: {aqi} ({levels[aqi]})\nPM2.5: {round(pm25)} µg/m³", text_color=color)

if __name__ == "__main__":
    app = VertexWeatherApp()
    app.mainloop()