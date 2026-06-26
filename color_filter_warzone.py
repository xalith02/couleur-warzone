#!/usr/bin/env python3
"""
🎮 Color Filter Pro - Warzone Edition
Application d'optimisation des couleurs et contraste en temps réel pour Warzone
"""

import cv2
import numpy as np
from tkinter import Tk, Scale, Label, Button, Frame, HORIZONTAL, LEFT
from tkinter import ttk
import threading
from PIL import Image, ImageTk
import sys

class ColorFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Color Filter Pro - Warzone Edition")
        self.root.geometry("950x850")
        self.root.configure(bg='#1a1a1a')
        
        # Variables de contrôle
        self.contrast = 1.0
        self.brightness = 1.0
        self.saturation = 1.0
        self.hue_shift = 0
        self.vibrance = 1.0
        self.sharpness = 1.0
        self.blur = 0
        self.gamma = 1.0
        self.color_boost = 1.0
        
        self.running = False
        self.cap = None
        self.preview_label = None
        self.sliders_dict = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Titre principal
        title = Label(self.root, text="🎨 COLOR FILTER PRO - WARZONE EDITION", 
                     font=("Arial", 16, "bold"), bg='#1a1a1a', fg='#00ff00')
        title.pack(pady=10)
        
        # Sous-titre
        subtitle = Label(self.root, text="Optimise tes visuels pour des performances EXTRÊMES 🚀", 
                        font=("Arial", 10), bg='#1a1a1a', fg='#888888')
        subtitle.pack(pady=3)
        
        # Frame scrollable pour les sliders
        main_frame = Frame(self.root, bg='#1a1a1a')
        main_frame.pack(padx=10, pady=5, fill="both", expand=False)
        
        # Titre des contrôles
        controls_title = Label(main_frame, text="⚙️ CONTRÔLES", 
                              font=("Arial", 12, "bold"), bg='#1a1a1a', fg='#00ff00')
        controls_title.pack(pady=8)
        
        # Créer les sliders
        self.sliders_dict['contrast'] = self.create_slider(main_frame, "🎯 Contraste", 0.5, 3.0, 1.0)
        self.sliders_dict['brightness'] = self.create_slider(main_frame, "💡 Luminosité", 0.5, 2.0, 1.0)
        self.sliders_dict['saturation'] = self.create_slider(main_frame, "🎨 Saturation", 0.0, 2.5, 1.0)
        self.sliders_dict['vibrance'] = self.create_slider(main_frame, "✨ Vibrance", 0.0, 2.0, 1.0)
        self.sliders_dict['color_boost'] = self.create_slider(main_frame, "🌈 Boost Couleur", 0.5, 3.0, 1.0)
        self.sliders_dict['sharpness'] = self.create_slider(main_frame, "🔪 Netteté", 0.0, 2.5, 1.0)
        self.sliders_dict['blur'] = self.create_slider(main_frame, "🌫️ Flou", 0, 10, 0)
        self.sliders_dict['gamma'] = self.create_slider(main_frame, "⚡ Gamma", 0.5, 2.5, 1.0)
        self.sliders_dict['hue_shift'] = self.create_slider(main_frame, "🎭 Décalage Teinte", -180, 180, 0)
        
        # Frame pour les boutons de contrôle
        control_frame = Frame(self.root, bg='#1a1a1a')
        control_frame.pack(pady=8)
        
        self.start_btn = Button(control_frame, text="▶ DÉMARRER CAPTURE", 
                               command=self.start_capture, bg='#00ff00', fg='#000000',
                               font=("Arial", 11, "bold"), padx=15, pady=8, cursor="hand2")
        self.start_btn.pack(side=LEFT, padx=5)
        
        self.stop_btn = Button(control_frame, text="⏹ ARRÊTER", 
                              command=self.stop_capture, bg='#ff0000', fg='#ffffff',
                              font=("Arial", 11, "bold"), padx=15, pady=8, state="disabled", cursor="hand2")
        self.stop_btn.pack(side=LEFT, padx=5)
        
        reset_btn = Button(control_frame, text="🔄 RÉINITIALISER", 
                          command=self.reset_values, bg='#ffff00', fg='#000000',
                          font=("Arial", 11, "bold"), padx=15, pady=8, cursor="hand2")
        reset_btn.pack(side=LEFT, padx=5)
        
        # Frame pour les presets
        preset_frame = Frame(self.root, bg='#1a1a1a')
        preset_frame.pack(pady=8)
        
        Label(preset_frame, text="🎯 PRESETS WARZONE:", font=("Arial", 11, "bold"), 
              bg='#1a1a1a', fg='#00ff00').pack(side=LEFT, padx=5)
        
        Button(preset_frame, text="🏆 COMPÉTITIF", command=self.preset_competitive,
              bg='#ff6600', fg='#ffffff', font=("Arial", 9, "bold"), padx=10, cursor="hand2").pack(side=LEFT, padx=2)
        
        Button(preset_frame, text="🌈 VIBRANT", command=self.preset_vibrant,
              bg='#ff00ff', fg='#ffffff', font=("Arial", 9, "bold"), padx=10, cursor="hand2").pack(side=LEFT, padx=2)
        
        Button(preset_frame, text="💡 HDR", command=self.preset_hdr,
              bg='#00ffff', fg='#000000', font=("Arial", 9, "bold"), padx=10, cursor="hand2").pack(side=LEFT, padx=2)
        
        Button(preset_frame, text="🎬 CINÉMATIQUE", command=self.preset_cinematic,
              bg='#ff0080', fg='#ffffff', font=("Arial", 9, "bold"), padx=10, cursor="hand2").pack(side=LEFT, padx=2)
        
        Button(preset_frame, text="🚀 ULTRA CONTRASTE", command=self.preset_ultra,
              bg='#00ff00', fg='#000000', font=("Arial", 9, "bold"), padx=10, cursor="hand2").pack(side=LEFT, padx=2)
        
        # Info zone
        info_frame = Frame(self.root, bg='#1a1a1a')
        info_frame.pack(pady=5)
        
        info_label = Label(info_frame, text="💻 Webcam: En attente... | 🎮 FPS: -- | 📊 Résolution: 640x480", 
                          font=("Arial", 9), bg='#1a1a1a', fg='#888888')
        info_label.pack()
        self.info_label = info_label
        
        # Preview video
        preview_frame = Frame(self.root, bg='#000000', borderwidth=3, relief="sunken")
        preview_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.preview_label = Label(preview_frame, bg='#000000', width=100, height=20)
        self.preview_label.pack()
        
    def create_slider(self, parent, label, from_, to, default):
        """Crée un slider avec label et affichage de valeur"""
        frame = Frame(parent, bg='#1a1a1a')
        frame.pack(fill="x", pady=3)
        
        lbl = Label(frame, text=label, width=20, font=("Arial", 9, "bold"), 
                   bg='#1a1a1a', fg='#ffffff', anchor="w")
        lbl.pack(side=LEFT, padx=5)
        
        slider = Scale(frame, from_=from_, to=to, orient=HORIZONTAL, 
                      bg='#333333', fg='#00ff00', troughcolor='#1a1a1a', 
                      length=350, highlightthickness=0, bd=0,
                      command=self.update_filter)
        slider.set(default)
        slider.pack(side=LEFT, fill="x", expand=True, padx=5)
        
        value_label = Label(frame, text=f"{default:.2f}", width=8, 
                           font=("Arial", 9, "bold"), bg='#1a1a1a', fg='#00ff00')
        value_label.pack(side="right", padx=5)
        
        return slider
        
    def update_filter(self, val=None):
        """Mise à jour des valeurs depuis les sliders"""
        self.contrast = float(self.sliders_dict['contrast'].get())
        self.brightness = float(self.sliders_dict['brightness'].get())
        self.saturation = float(self.sliders_dict['saturation'].get())
        self.vibrance = float(self.sliders_dict['vibrance'].get())
        self.color_boost = float(self.sliders_dict['color_boost'].get())
        self.sharpness = float(self.sliders_dict['sharpness'].get())
        self.blur = int(float(self.sliders_dict['blur'].get()))
        self.gamma = float(self.sliders_dict['gamma'].get())
        self.hue_shift = int(float(self.sliders_dict['hue_shift'].get()))
    
    def apply_filters(self, frame):
        """Applique tous les filtres à l'image"""
        # Convertir en float pour les calculs
        img = frame.astype(np.float32) / 255.0
        
        # Appliquer Gamma
        img = np.power(np.clip(img, 0.001, 1), 1.0 / max(self.gamma, 0.1))
        
        # Convertir BGR to HSV
        img_uint8 = np.clip(img * 255, 0, 255).astype(np.uint8)
        hsv = cv2.cvtColor(img_uint8, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Ajuster la saturation
        hsv[:,:,1] = np.clip(hsv[:,:,1] * self.saturation, 0, 255)
        
        # Ajuster la teinte
        hsv[:,:,0] = (hsv[:,:,0] + self.hue_shift) % 180
        
        # Appliquer la vibrance
        hsv[:,:,1] = np.clip(hsv[:,:,1] * self.vibrance, 0, 255)
        
        # Convertir back to BGR
        img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32) / 255.0
        
        # Appliquer la luminosité
        img = np.clip(img * self.brightness, 0, 1)
        
        # Appliquer le contraste
        img = np.clip((img - 0.5) * self.contrast + 0.5, 0, 1)
        
        # Appliquer le boost de couleur
        img = np.clip(img * self.color_boost, 0, 1)
        
        # Appliquer la netteté
        if self.sharpness > 1.0:
            kernel = np.array([[-1, -1, -1],
                             [-1, 9*self.sharpness, -1],
                             [-1, -1, -1]]) / (1 + 8*self.sharpness)
            img_uint8 = np.clip(img * 255, 0, 255).astype(np.uint8)
            img_uint8 = cv2.filter2D(img_uint8, -1, kernel)
            img = img_uint8.astype(np.float32) / 255.0
        
        # Appliquer le flou
        if self.blur > 0:
            blur_size = int(self.blur * 2 + 1)
            img = cv2.GaussianBlur(img, (blur_size, blur_size), 0)
        
        return np.clip(img * 255, 0, 255).astype(np.uint8)
    
    def start_capture(self):
        """Démarre la capture vidéo"""
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        thread = threading.Thread(target=self.capture_loop, daemon=True)
        thread.start()
        
    def stop_capture(self):
        """Arrête la capture vidéo"""
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        if self.cap:
            self.cap.release()
    
    def capture_loop(self):
        """Boucle principale de capture et traitement"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.preview_label.config(text="⚠️ ERREUR: Webcam non trouvée!")
            return
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        frame_count = 0
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Mettre à jour les filtres
            self.update_filter()
            
            # Appliquer les filtres
            filtered = self.apply_filters(frame)
            
            # Convertir pour l'affichage
            rgb = cv2.cvtColor(filtered, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            img.thumbnail((640, 480), Image.Resampling.LANCZOS)
            
            # Afficher l'image
            photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=photo)
            self.preview_label.image = photo
            
            # Mettre à jour l'info
            if frame_count % 10 == 0:
                self.info_label.config(
                    text=f"💻 Webcam: Connectée ✓ | 🎮 FPS: ~30 | 📊 Résolution: 640x480"
                )
            
            try:
                self.root.update()
            except:
                break
    
    def set_all_values(self, contrast, brightness, saturation, vibrance, color_boost, sharpness, blur, gamma, hue_shift):
        """Définit toutes les valeurs des sliders"""
        self.sliders_dict['contrast'].set(contrast)
        self.sliders_dict['brightness'].set(brightness)
        self.sliders_dict['saturation'].set(saturation)
        self.sliders_dict['vibrance'].set(vibrance)
        self.sliders_dict['color_boost'].set(color_boost)
        self.sliders_dict['sharpness'].set(sharpness)
        self.sliders_dict['blur'].set(blur)
        self.sliders_dict['gamma'].set(gamma)
        self.sliders_dict['hue_shift'].set(hue_shift)
        self.update_filter()
    
    def reset_values(self):
        """Réinitialise toutes les valeurs par défaut"""
        self.set_all_values(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0, 1.0, 0)
    
    def preset_competitive(self):
        """Preset optimisé pour la compétition - Maximum de visibilité"""
        self.set_all_values(1.8, 1.0, 1.2, 1.0, 1.4, 1.6, 0, 1.0, 0)
    
    def preset_vibrant(self):
        """Preset vibrant - Couleurs éclatantes et détaillées"""
        self.set_all_values(1.3, 1.0, 2.5, 2.0, 1.8, 1.3, 0, 1.0, 0)
    
    def preset_hdr(self):
        """Preset HDR - Rendu cinématique professionnel"""
        self.set_all_values(1.4, 1.2, 1.5, 1.3, 1.3, 1.4, 0, 0.7, 0)
    
    def preset_cinematic(self):
        """Preset cinématique - Style film hollywoodien"""
        self.set_all_values(1.2, 1.15, 1.8, 1.5, 1.4, 1.1, 0, 0.75, 0)
    
    def preset_ultra(self):
        """Preset ultra contraste - Contraste extrême pour la compétition hardcore"""
        self.set_all_values(2.2, 1.0, 1.4, 1.2, 1.5, 1.8, 0, 1.0, 0)

def main():
    """Fonction principale"""
    root = Tk()
    app = ColorFilterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()