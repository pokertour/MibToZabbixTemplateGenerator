import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import uuid
import yaml
import os
import time
from collections import Counter

APP_VERSION = "1.0.5"

TRANSLATIONS = {
    "FR": {
        "title_main": "MibToZabbixTemplateGenerator",
        "title_preview": "Aperçu & Édition des Items",
        "config_header": "Configuration du Template",
        "btn_load": "Charger MIB",
        "no_file": "Aucun fichier sélectionné",
        "lbl_template_name": "Nom du Template :",
        "placeholder_template": "Mon Equipement SNMP",
        "lbl_zabbix_version": "Version Zabbix :",
        "lbl_zabbix_group": "Groupe Zabbix :",
        "placeholder_group": "Templates",
        "lbl_base_oid": "OID Racine (Base) :",
        "lbl_delay": "Intervalle d'actualisation :",
        "lbl_help_oid": "(Ex: Pour Christie CP4415 -> .1.3.6.1.4.1.25766.1.12.1.157)",
        "lbl_detected_root": "OID Racine détecté :",
        "lbl_no_root": "Racine non détectée, veuillez la saisir",
        "list_header": "Objets détectés (Sélectionnez pour inclure)",
        "search_label": "Rechercher : ",
        "search_placeholder": "Rechercher par nom ou description...",
        "col_name": "Nom de l'Objet",
        "col_oid": "OID SNMP",
        "col_syntax": "Type (Syntax)",
        "col_desc": "Description",
        "btn_select_all": "TOUT SÉLECTIONNER",
        "btn_deselect_all": "TOUT DÉSELECTIONNER",
        "col_select": "Sél.",
        "btn_preview_export": "AVANT-PROPOS & EXPORT",
        "msg_error": "Erreur",
        "msg_warn": "Attention",
        "msg_success": "Succès",
        "msg_no_selection": "Veuillez sélectionner au moins un objet dans la liste.",
        "msg_no_root": "Veuillez définir l'OID Racine.",
        "msg_saved": "Fichier sauvegardé avec succès !",
        "preview_header": "Personnalisez vos items avant l'exportation",
        "lbl_name": "Nom:",
        "lbl_key": "Clé:",
        "lbl_desc": "Desc:",
        "lbl_tags": "Tags:",
        "btn_cancel": "Annuler",
        "btn_final_export": "EXPORTER LE YAML FINAL",
        "msg_mib_success": "objets trouvés dans la MIB."
    },
    "EN": {
        "title_main": "MibToZabbixTemplateGenerator",
        "title_preview": "Preview & Edit Items",
        "config_header": "Template Configuration",
        "btn_load": "Load MIB",
        "no_file": "No file selected",
        "lbl_template_name": "Template Name:",
        "placeholder_template": "My SNMP Device",
        "lbl_zabbix_version": "Zabbix Version:",
        "lbl_zabbix_group": "Zabbix Group:",
        "placeholder_group": "Templates",
        "lbl_base_oid": "Root OID (Base):",
        "lbl_delay": "Update interval:",
        "lbl_help_oid": "(Ex: For Christie CP4415 -> .1.3.6.1.4.1.25766.1.12.1.157)",
        "lbl_detected_root": "Root OID detected:",
        "lbl_no_root": "Root not detected, please enter manually",
        "list_header": "Detected Objects (Select to include)",
        "search_label": "Search: ",
        "search_placeholder": "Search by name or description...",
        "col_name": "Object Name",
        "col_oid": "SNMP OID",
        "col_syntax": "Type (Syntax)",
        "col_desc": "Description",
        "btn_select_all": "SELECT ALL",
        "btn_deselect_all": "DESELECT ALL",
        "col_select": "Sel.",
        "btn_preview_export": "PREVIEW & EXPORT",
        "msg_error": "Error",
        "msg_warn": "Warning",
        "msg_success": "Success",
        "msg_no_selection": "Please select at least one object from the list.",
        "msg_no_root": "Please define the Root OID.",
        "msg_saved": "File saved successfully!",
        "preview_header": "Customize your items before export",
        "lbl_name": "Name:",
        "lbl_key": "Key:",
        "lbl_desc": "Desc:",
        "lbl_tags": "Tags:",
        "btn_cancel": "Cancel",
        "btn_final_export": "EXPORT FINAL YAML",
        "msg_mib_success": "objects found in MIB."
    }
}

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PreviewWindow(ctk.CTkToplevel):
    def __init__(self, parent, selected_items, base_oid, template_name, group_name, zabbix_version, default_delay="8h", lang="FR"):
        super().__init__(parent)
        self.lang = lang
        self.t = TRANSLATIONS[lang]
        self.title(f"{self.t['title_preview']} - v{APP_VERSION}")
        self.geometry("1100x800")
        self.parent = parent
        self.selected_items = selected_items
        self.base_oid = base_oid
        self.template_name = template_name
        self.group_name = group_name
        self.zabbix_version = zabbix_version
        self.default_delay = default_delay

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.label = ctk.CTkLabel(self, text=self.t['preview_header'], font=ctk.CTkFont(size=18, weight="bold"))
        self.label.grid(row=0, column=0, padx=20, pady=20)

        # Scrollable Frame for items
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(1, weight=1)

        self.item_widgets = []
        for i, item in enumerate(self.selected_items):
            frame = ctk.CTkFrame(self.scroll_frame, corner_radius=5)
            frame.pack(fill="x", padx=5, pady=5)
            
            # OID Label
            full_oid = item.get('resolved_oid', f"{self.base_oid}.{item['suffix']}.0")
            ctk.CTkLabel(frame, text=f"OID: {full_oid}", font=ctk.CTkFont(size=11, weight="bold"), text_color="#3b8ed0").grid(row=0, column=0, columnspan=2, padx=10, pady=(5,0), sticky="w")

            # Name
            ctk.CTkLabel(frame, text=self.t['lbl_name']).grid(row=1, column=0, padx=5, pady=5, sticky="e")
            name_entry = ctk.CTkEntry(frame, width=300)
            name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
            name_entry.insert(0, item['name'])
            
            # Key
            ctk.CTkLabel(frame, text=self.t['lbl_key']).grid(row=1, column=2, padx=5, pady=5, sticky="e")
            key_entry = ctk.CTkEntry(frame, width=250)
            key_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
            
            # Default key for traps vs items
            default_key = f"snmptrap[{item['name'].lower()}]" if item.get('is_trap') else f"snmp.{item['name'].lower()}"
            key_entry.insert(0, default_key)
            
            # Description
            ctk.CTkLabel(frame, text=self.t['lbl_desc']).grid(row=2, column=0, padx=5, pady=5, sticky="e")
            desc_entry = ctk.CTkEntry(frame, width=300)
            desc_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
            desc_entry.insert(0, item['desc'])

            # Tags
            ctk.CTkLabel(frame, text=self.t['lbl_tags']).grid(row=2, column=2, padx=5, pady=5, sticky="e")
            tags_entry = ctk.CTkEntry(frame, width=300, placeholder_text="component:mib-import, device:snmp")
            tags_entry.grid(row=2, column=3, padx=5, pady=5, sticky="w")
            tags_entry.insert(0, "component:mib-import")

            # Delay
            ctk.CTkLabel(frame, text="Delay:").grid(row=1, column=4, padx=5, pady=5, sticky="e")
            delay_entry = ctk.CTkEntry(frame, width=80)
            delay_entry.grid(row=1, column=5, padx=5, pady=5, sticky="w")
            delay_entry.insert(0, self.default_delay)
            
            self.item_widgets.append({
                "item_id": item['id'],
                "suffix": item['suffix'],
                "syntax": item['syntax'],
                "is_trap": item.get('is_trap', False),
                "resolved_oid": item.get('resolved_oid'),
                "name_entry": name_entry,
                "key_entry": key_entry,
                "desc_entry": desc_entry,
                "tags_entry": tags_entry,
                "delay_entry": delay_entry
            })

        # Actions
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        
        self.btn_cancel = ctk.CTkButton(self.btn_frame, text=self.t['btn_cancel'], fg_color="gray", command=self.destroy)
        self.btn_cancel.pack(side="left", padx=20)
        
        self.btn_save = ctk.CTkButton(self.btn_frame, text=self.t['btn_final_export'], fg_color="#28a745", command=self.final_export)
        self.btn_save.pack(side="right", padx=20)

    def final_export(self):
        zbx_template = {
            "zabbix_export": {
                "version": self.zabbix_version,
                "template_groups": [
                    {"uuid": str(uuid.uuid4()).replace('-', ''), "name": self.group_name}
                ],
                "templates": [
                    {
                        "uuid": str(uuid.uuid4()).replace('-', ''),
                        "template": self.template_name,
                        "name": self.template_name,
                        "description": f"Généré automatiquement depuis MIB.\nBase OID: {self.base_oid}",
                        "groups": [{"name": self.group_name}],
                        "items": []
                    }
                ]
            }
        }

        for w in self.item_widgets:
            name = w['name_entry'].get()
            key = w['key_entry'].get()
            desc = w['desc_entry'].get()
            tags_raw = w['tags_entry'].get()
            delay = w['delay_entry'].get() or self.default_delay
            
            # Utiliser l'OID résolu ou affiché
            full_oid = w.get('resolved_oid')
            if not full_oid:
                full_oid = f"{self.base_oid}.{w['suffix']}.0"
            
            # Si l'OID contient encore XXXX, on essaie de le remplacer par la base OID actuelle (cas du fallback)
            if ".1.3.6.1.4.1.XXXX" in full_oid:
                 full_oid = full_oid.replace(".1.3.6.1.4.1.XXXX", self.base_oid)
            
            # Parse tags
            zbx_tags = []
            if tags_raw:
                parts = tags_raw.split(',')
                for p in parts:
                    if ':' in p:
                        t, v = p.split(':', 1)
                        zbx_tags.append({"tag": t.strip(), "value": v.strip()})

            zbx_item = {
                "uuid": str(uuid.uuid4()).replace('-', ''),
                "name": name,
                "type": "SNMP_TRAP" if w.get('is_trap') else "SNMP_AGENT",
                "snmp_oid": full_oid,
                "key": key,
                "delay": delay,
                "history": "7d",
                "trends": "90d",
                "value_type": self.parent.get_zabbix_type(w['syntax']),
                "description": desc,
                "tags": zbx_tags
            }
            
            # Simple units detection from description
            desc_l = desc.lower()
            if "percent" in desc_l or "%" in desc_l:
                zbx_item["units"] = "%"
            elif any(x in desc_l for x in ["celsius", "centigrade", "temperature"]):
                zbx_item["units"] = "C"
                
            zbx_template["zabbix_export"]["templates"][0]["items"].append(zbx_item)

        # Suggest a safe filename based on template name
        suggested_filename = re.sub(r'[^\w\d-]', '_', self.template_name) + ".yaml"

        file_path = filedialog.asksaveasfilename(
            parent=self,
            initialfile=suggested_filename,
            defaultextension=".yaml", 
            filetypes=[("YAML files", "*.yaml")]
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(zbx_template, f, sort_keys=False, allow_unicode=True)
            
            messagebox.showinfo(self.t['msg_success'], self.t['msg_saved'], parent=self)
            self.destroy()

class MibToZabbixApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.lang = "FR"
        self.t = TRANSLATIONS[self.lang]

        self.title(f"{self.t['title_main']} - v{APP_VERSION}")
        self.geometry("1100x900")

        # Variables
        self.mib_content = ""
        self.parsed_items = []
        self.last_clicked_id = None
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Top Section: Configuration ---
        self.config_frame = ctk.CTkFrame(self, corner_radius=10)
        self.config_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        self.config_frame.grid_columnconfigure(1, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(self.config_frame, text=self.t['config_header'], font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="w")

        # Language Selector (New)
        self.lang_var = ctk.StringVar(value="FR")
        self.lang_switch = ctk.CTkSegmentedButton(self.config_frame, values=["FR", "EN"], 
                                                  command=self.change_language, variable=self.lang_var)
        self.lang_switch.grid(row=0, column=1, padx=20, pady=10, sticky="e")

        # MIB File Selection
        self.btn_load = ctk.CTkButton(self.config_frame, text=self.t['btn_load'], command=self.load_mib)
        self.btn_load.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.lbl_filename = ctk.CTkLabel(self.config_frame, text=self.t['no_file'], text_color="gray")
        self.lbl_filename.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        # Entries
        self.label_tpl = ctk.CTkLabel(self.config_frame, text=self.t['lbl_template_name'])
        self.label_tpl.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.entry_tpl_name = ctk.CTkEntry(self.config_frame, width=500, placeholder_text=self.t['placeholder_template'])
        self.entry_tpl_name.grid(row=2, column=1, padx=20, pady=5, sticky="w")
        self.entry_tpl_name.insert(0, self.t['placeholder_template'])

        self.label_version = ctk.CTkLabel(self.config_frame, text=self.t['lbl_zabbix_version'])
        self.label_version.grid(row=3, column=0, padx=20, pady=5, sticky="w")
        self.entry_version = ctk.CTkEntry(self.config_frame, width=100)
        self.entry_version.grid(row=3, column=1, padx=20, pady=5, sticky="w")
        self.entry_version.insert(0, "7.0")

        self.label_delay = ctk.CTkLabel(self.config_frame, text=self.t['lbl_delay'])
        self.label_delay.grid(row=3, column=1, padx=(150, 20), pady=5, sticky="w")
        self.entry_delay = ctk.CTkEntry(self.config_frame, width=100)
        self.entry_delay.grid(row=3, column=1, padx=(320, 20), pady=5, sticky="w")
        self.entry_delay.insert(0, "8h")

        self.label_group = ctk.CTkLabel(self.config_frame, text=self.t['lbl_zabbix_group'])
        self.label_group.grid(row=4, column=0, padx=20, pady=5, sticky="w")
        self.entry_group = ctk.CTkEntry(self.config_frame, width=500, placeholder_text=self.t['placeholder_group'])
        self.entry_group.grid(row=4, column=1, padx=20, pady=5, sticky="w")
        self.entry_group.insert(0, self.t['placeholder_group'])

        self.label_oid = ctk.CTkLabel(self.config_frame, text=self.t['lbl_base_oid'])
        self.label_oid.grid(row=5, column=0, padx=20, pady=5, sticky="w")
        self.entry_base_oid = ctk.CTkEntry(self.config_frame, width=500, placeholder_text="1.3.6.1.4.1.XXXX")
        self.entry_base_oid.grid(row=5, column=1, padx=20, pady=5, sticky="w")
        self.entry_base_oid.insert(0, "1.3.6.1.4.1.XXXX")
        self.entry_base_oid.bind("<KeyRelease>", self.update_oids)
        
        self.lbl_help = ctk.CTkLabel(self.config_frame, text=self.t['lbl_help_oid'], 
                                      font=ctk.CTkFont(size=11), text_color="#3b8ed0")
        self.lbl_help.grid(row=6, column=1, padx=20, pady=(0, 10), sticky="w")

        # --- Middle Section: List of items ---
        self.list_frame = ctk.CTkFrame(self, corner_radius=10)
        self.list_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_rowconfigure(1, weight=1)

        self.list_header = ctk.CTkLabel(self.list_frame, text=self.t['list_header'], font=ctk.CTkFont(size=16, weight="bold"))
        self.list_header.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Search Bar (New)
        self.search_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        self.search_frame.grid(row=0, column=0, padx=(0, 20), pady=10, sticky="e")
        
        self.entry_search = ctk.CTkEntry(self.search_frame, width=300, placeholder_text=self.t['search_placeholder'])
        self.entry_search.pack(side="right")
        self.entry_search.bind("<KeyRelease>", self.filter_items)
        self.lbl_search = ctk.CTkLabel(self.search_frame, text=self.t['search_label'])
        self.lbl_search.pack(side="right", padx=5)

        # Treeview Scrollbar Container
        self.tree_container = tk.Frame(self.list_frame, background="#2b2b2b")
        self.tree_container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.tree_container.grid_columnconfigure(0, weight=1)
        self.tree_container.grid_rowconfigure(0, weight=1)

        # Treeview Style
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        borderwidth=0)
        style.map("Treeview", background=[('selected', '#3b8ed0')])
        style.configure("Treeview.Heading", background="#333333", foreground="white", borderwidth=0)

        columns = ("selection", "name", "oid", "syntax", "desc")
        self.tree = ttk.Treeview(self.tree_container, columns=columns, show='headings', selectmode="browse")
        
        self.tree.heading("selection", text=self.t['col_select'])
        self.tree.heading("name", text=self.t['col_name'])
        self.tree.heading("oid", text=self.t['col_oid'])
        self.tree.heading("syntax", text=self.t['col_syntax'])
        self.tree.heading("desc", text=self.t['col_desc'])
        
        self.tree.column("selection", width=40, anchor="center")
        self.tree.column("name", width=250)
        self.tree.column("oid", width=250)
        self.tree.column("syntax", width=150)
        self.tree.column("desc", width=600)

        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)

        # Vertical Scrollbar
        self.v_scrollbar = ctk.CTkScrollbar(self.tree_container, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=self.v_scrollbar.set)
        
        # Horizontal Scrollbar
        self.h_scrollbar = ctk.CTkScrollbar(self.tree_container, orientation="horizontal", command=self.tree.xview)
        self.tree.configure(xscroll=self.h_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # --- Bottom Section: Actions ---
        self.action_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.action_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        self.btn_select_all = ctk.CTkButton(self.action_frame, text=self.t['btn_select_all'], fg_color="gray", hover_color="#555555", command=self.select_all)
        self.btn_select_all.pack(side="left", padx=20)

        # Progress Bar (New)
        self.progress_bar = ctk.CTkProgressBar(self.action_frame, width=300)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="left", padx=20)
        self.progress_bar.pack_forget() # Hidden by default

        self.btn_generate = ctk.CTkButton(self.action_frame, text=self.t['btn_preview_export'], font=ctk.CTkFont(weight="bold"), 
                                          fg_color="#28a745", hover_color="#218838", command=self.generate_yaml)
        self.btn_generate.pack(side="right", padx=20)

        # Version label (Bottom Right)
        self.lbl_version_footer = ctk.CTkLabel(self, text=f"v{APP_VERSION}", font=ctk.CTkFont(size=10), text_color="gray")
        self.lbl_version_footer.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5)

    def change_language(self, new_lang):
        self.lang = new_lang
        self.update_ui()

    def update_ui(self):
        self.t = TRANSLATIONS[self.lang]
        self.title(f"{self.t['title_main']} - v{APP_VERSION}")
        
        # Config Frame
        self.title_label.configure(text=self.t['config_header'])
        self.btn_load.configure(text=self.t['btn_load'])
        self.lbl_filename.configure(text=self.t['no_file'] if not self.mib_content else self.lbl_filename.cget("text"))
        self.label_tpl.configure(text=self.t['lbl_template_name'])
        self.entry_tpl_name.configure(placeholder_text=self.t['placeholder_template'])
        self.label_version.configure(text=self.t['lbl_zabbix_version'])
        self.label_group.configure(text=self.t['lbl_zabbix_group'])
        self.entry_group.configure(placeholder_text=self.t['placeholder_group'])
        self.label_delay.configure(text=self.t['lbl_delay'])
        self.label_oid.configure(text=self.t['lbl_base_oid'])
        self.lbl_help.configure(text=self.t['lbl_help_oid'])
        
        # List Frame
        self.list_header.configure(text=self.t['list_header'])
        self.entry_search.configure(placeholder_text=self.t['search_placeholder'])
        self.lbl_search.configure(text=self.t['search_label'])
        
        # Treeview
        self.tree.heading("selection", text=self.t['col_select'])
        self.tree.heading("name", text=self.t['col_name'])
        self.tree.heading("oid", text=self.t['col_oid'])
        self.tree.heading("syntax", text=self.t['col_syntax'])
        self.tree.heading("desc", text=self.t['col_desc'])
        
        # Action Frame
        self.btn_select_all.configure(text=self.t['btn_select_all'])
        self.btn_generate.configure(text=self.t['btn_preview_export'])

    def load_mib(self):
        filename = filedialog.askopenfilename(filetypes=[("MIB Files", "*.mib"), ("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filename:
            return
        
        self.lbl_filename.configure(text=os.path.basename(filename), text_color="white")
        
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                self.mib_content = f.read()
            self.parse_mib()
        except Exception as e:
            messagebox.showerror(self.t['msg_error'], f"Impossible de lire le fichier / Cannot read file : {e}")

    def parse_mib(self):
        """
        Parser Regex pour extraire les OBJECT-TYPE et tenter de deviner l'OID Racine.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.parsed_items = []
        self.last_clicked_id = None

        # --- Détection Robuste de l'OID Racine ---
        # 1. Dictionnaire des identifiants OID connus
        known_oids = {
            "iso": ".1",
            "org": ".1.3",
            "dod": ".1.3.6",
            "internet": ".1.3.6.1",
            "directory": ".1.3.6.1.1",
            "mgmt": ".1.3.6.1.2",
            "mib-2": ".1.3.6.1.2.1",
            "transmission": ".1.3.6.1.2.1.10",
            "experimental": ".1.3.6.1.3",
            "private": ".1.3.6.1.4",
            "enterprises": ".1.3.6.1.4.1",
            "security": ".1.3.6.1.5",
            "snmpv2": ".1.3.6.1.6",
            "snmpModules": ".1.3.6.1.6.3",
        }

        # --- NOUVEAU: Extraction des OIDs depuis les commentaires (style Barco) ---
        # Cherche "-- 1.3.6..." suivi par le nom de l'objet sur la ligne suivante
        comment_oid_pattern = re.compile(r'--\s+([\d\.]+)\s*\n\s*([\w\d\-]+)', re.MULTILINE)
        for oid_val, name in comment_oid_pattern.findall(self.mib_content):
            if not oid_val.startswith("."):
                oid_val = "." + oid_val
            known_oids[name] = oid_val

        # 2. Extraire tous les IDENTIFIANTS (OBJECT IDENTIFIER, MODULE-IDENTITY et OBJECT-TYPE pour la hiérarchie)
        hierarchy_pattern = re.compile(r'^\s*([\w\d\-]+)\s+(?:OBJECT IDENTIFIER|MODULE-IDENTITY|OBJECT-TYPE|OBJECT-IDENTITY).*?::=\s+\{\s*([\w\d\-]+)\s+(\d+)\s*\}', re.DOTALL | re.IGNORECASE | re.MULTILINE)
        all_definitions = hierarchy_pattern.findall(self.mib_content)
        
        # On ajoute aussi les définitions de type { 1 2 3 }
        full_numeric_pattern = re.compile(r'^\s*([\w\d\-]+)\s+(?:OBJECT IDENTIFIER|MODULE-IDENTITY).*?::=\s+\{\s*([\d\s]+)\s*\}', re.DOTALL | re.IGNORECASE | re.MULTILINE)
        numeric_definitions = full_numeric_pattern.findall(self.mib_content)
        for name, content in numeric_definitions:
            oid_val = "." + ".".join(content.split())
            known_oids[name] = oid_val

        # On fait plusieurs passes pour résoudre les dépendances (jusqu'à ce que plus rien ne bouge ou max 20 passes pour MIB complexes)
        for _ in range(20):
            changed = False
            for name, parent, suffix in all_definitions:
                if name not in known_oids:
                    if parent in known_oids:
                        known_oids[name] = f"{known_oids[parent]}.{suffix}"
                        changed = True
                elif not known_oids[name].startswith("."): # Tenter de compléter si non absolu
                     if parent in known_oids and known_oids[parent].startswith("."):
                        known_oids[name] = f"{known_oids[parent]}.{suffix}"
                        changed = True
            if not changed: break

        # 3. Trouver le point de départ le plus probable pour le template
        # On cherche l'OID d'entreprise le plus long
        suggested_root = ".1.3.6.1.4.1.XXXX"
        
        # On cherche un OID qui ressemble à une racine d'entreprise (1.3.6.1.4.1.N)
        potential_roots = []
        for val in known_oids.values():
            if val.startswith(".1.3.6.1.4.1."):
                parts = val.split('.')
                if len(parts) >= 7: # . 1 3 6 1 4 1 N
                    potential_roots.append(".".join(parts[:8])) # Jusqu'au 14988 par exemple
        
        if potential_roots:
            suggested_root = Counter(potential_roots).most_common(1)[0][0]

        self.entry_base_oid.delete(0, tk.END)
        self.entry_base_oid.insert(0, suggested_root)
        if "XXXX" not in suggested_root:
            self.lbl_help.configure(text=f"({self.t['lbl_detected_root']} {suggested_root})", text_color="#28a745")
        else:
            self.lbl_help.configure(text=f"({self.t['lbl_no_root']})", text_color="#3b8ed0")

        # --- Fin Détection ---
        
        # Pattern pour OBJECT-TYPE (Items)
        # Amélioré pour capturer SYNTAX sur plusieurs lignes (ex: BITS)
        # Support des OIDs à plusieurs niveaux ::= { parent 1 2 }
        item_pattern = re.compile(
            r'^\s*([\w\d\-]+)\s+OBJECT-TYPE\s+.*?'
            r'SYNTAX\s+(.*?)\s+(?:MAX-ACCESS|ACCESS)\s+.*?'
            r'DESCRIPTION\s+\"(.*?)\"\s+.*?'
            r'::=\s+\{\s*([\w\d\-]+)\s+([\d\s]+)\s*\}',
            re.DOTALL | re.IGNORECASE | re.MULTILINE
        )

        # Pattern pour NOTIFICATION-TYPE / TRAP-TYPE (Traps)
        # Gestion des styles SNMPv1 (TRAP-TYPE) et SNMPv2 (NOTIFICATION-TYPE)
        # Très flexible sur ce qui se trouve entre la description et l'OID
        # Support des OIDs à plusieurs niveaux ::= { parent 1 2 }
        trap_pattern = re.compile(
            r'^\s*([\w\d\-]+)\s+(?:NOTIFICATION-TYPE|TRAP-TYPE)\s+.*?'
            r'(?:ENTERPRISE\s+([\w\d\-]+)\s+)?'
            r'(?:(?:OBJECTS|VARIABLES)\s+\{(.*?)\}\s+)?'
            r'DESCRIPTION\s+\"(.*?)\".*?'
            r'::=\s+(?:\{\s*([\w\d\-]+)\s+([\d\s]+)\s*\}|(\d+))',
            re.DOTALL | re.IGNORECASE | re.MULTILINE
        )

        matches_items = item_pattern.findall(self.mib_content)
        matches_traps = trap_pattern.findall(self.mib_content)
        
        if not matches_items and not matches_traps:
            messagebox.showwarning(self.t['msg_warn'], "Aucun objet standard trouvé / No standard objects found.")
            return

        count = 0
        base_oid_ui = self.entry_base_oid.get().strip()

        # Traitement des Items (OBJECT-TYPE)
        for name, syntax, desc, parent, suffix in matches_items:
            desc_clean = " ".join(desc.split())
            syntax_clean = syntax.strip()
            
            if "SEQUENCE" in syntax_clean:
                continue

            # Formater le suffixe pour gérer les niveaux multiples (ex: "0 1" -> "0.1")
            suffix_fmt = ".".join(suffix.split())

            # Résolution de l'OID (avec .0 pour les items scalaires)
            if name in known_oids and known_oids[name].startswith("."):
                full_oid = f"{known_oids[name]}.0"
            elif parent in known_oids and known_oids[parent].startswith("."):
                full_oid = f"{known_oids[parent]}.{suffix_fmt}.0"
            else:
                full_oid = f"{base_oid_ui}.{suffix_fmt}.0"
            
            self.tree.insert("", "end", iid=count, values=("☐", name, full_oid, syntax_clean, desc_clean))
            self.parsed_items.append({
                "id": count,
                "selected": False,
                "name": name,
                "parent": parent,
                "suffix": suffix_fmt,
                "syntax": syntax_clean,
                "desc": desc_clean,
                "resolved_oid": full_oid,
                "is_trap": False
            })
            count += 1

        # Traitement des Traps (NOTIFICATION-TYPE / TRAP-TYPE)
        # Structure de match : (name, enterprise, objects/vars, desc, parent_v2, suffix_v2, suffix_v1)
        for m in matches_traps:
            name, enterprise, objects, desc, parent_v2, suffix_v2, suffix_v1 = m
            desc_clean = " ".join(desc.split())
            
            # Détermination du parent et du suffixe selon le type de trap
            if suffix_v1:
                # Style SNMPv1 (TRAP-TYPE)
                parent = enterprise
                suffix = suffix_v1
            else:
                # Style SNMPv2 (NOTIFICATION-TYPE)
                parent = parent_v2
                suffix = suffix_v2

            # Formater le suffixe (ex: "0 1" -> "0.1")
            suffix_fmt = ".".join(suffix.split())

            # Résolution de l'OID (sans .0 pour les traps)
            if name in known_oids and known_oids[name].startswith("."):
                full_oid = known_oids[name]
            elif parent in known_oids and known_oids[parent].startswith("."):
                full_oid = f"{known_oids[parent]}.{suffix_fmt}"
            else:
                full_oid = f"{base_oid_ui}.{suffix_fmt}"
            
            self.tree.insert("", "end", iid=count, values=("☐", f"[TRAP] {name}", full_oid, "Trap", desc_clean))
            self.parsed_items.append({
                "id": count,
                "selected": False,
                "name": name,
                "parent": parent,
                "suffix": suffix,
                "syntax": "Trap",
                "desc": desc_clean,
                "resolved_oid": full_oid,
                "is_trap": True
            })
            count += 1
            
        messagebox.showinfo(self.t['msg_success'], f"{count} {self.t['msg_mib_success']}")

    def select_all(self):
        # Toggle based on first item if exists
        if not self.parsed_items:
            return
            
        all_selected = all(item['selected'] for item in self.parsed_items)
        new_state = not all_selected
        
        for item in self.parsed_items:
            item['selected'] = new_state
            
        self.filter_items() # Refresh display
        
        self.btn_select_all.configure(text=self.t['btn_deselect_all'] if new_state else self.t['btn_select_all'])

    def on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            return
            
        item_id_str = self.tree.identify_row(event.y)
        if not item_id_str:
            return
            
        column = self.tree.identify_column(event.x)
        
        # Toggle only if clicking the selection column (column #1)
        if column == "#1":
            try:
                iid = int(item_id_str)
                is_shift = event.state & 0x0001
                
                # Find current item
                curr_item = next((item for item in self.parsed_items if item['id'] == iid), None)
                if not curr_item:
                    return

                if is_shift and self.last_clicked_id is not None:
                    # Range selection
                    all_visible_iids = self.tree.get_children()
                    try:
                        start_idx = all_visible_iids.index(str(self.last_clicked_id))
                        end_idx = all_visible_iids.index(str(iid))
                        
                        if start_idx > end_idx:
                            start_idx, end_idx = end_idx, start_idx
                        
                        # Use the new target state (flipping the current state of the clicked item)
                        target_state = not curr_item['selected']
                        
                        for i in range(start_idx, end_idx + 1):
                            child_iid_str = all_visible_iids[i]
                            child_iid = int(child_iid_str)
                            child_item = next((item for item in self.parsed_items if item['id'] == child_iid), None)
                            if child_item:
                                child_item['selected'] = target_state
                                values = list(self.tree.item(child_iid_str, "values"))
                                values[0] = "☑" if target_state else "☐"
                                self.tree.item(child_iid_str, values=values)
                    except ValueError:
                        # Fallback if last_clicked_id is not visible
                        curr_item['selected'] = not curr_item['selected']
                        values = list(self.tree.item(item_id_str, "values"))
                        values[0] = "☑" if curr_item['selected'] else "☐"
                        self.tree.item(item_id_str, values=values)
                else:
                    # Normal toggle
                    curr_item['selected'] = not curr_item['selected']
                    values = list(self.tree.item(item_id_str, "values"))
                    values[0] = "☑" if curr_item['selected'] else "☐"
                    self.tree.item(item_id_str, values=values)
                
                self.last_clicked_id = iid
                
            except (ValueError, StopIteration):
                pass

    def update_oids(self, event=None):
        base_oid = self.entry_base_oid.get().strip()
        if base_oid and not base_oid.startswith("."):
            base_oid = "." + base_oid
            self.entry_base_oid.delete(0, tk.END)
            self.entry_base_oid.insert(0, base_oid)
        
        for item_id_str in self.tree.get_children():
            try:
                item_id = int(item_id_str)
                if item_id < len(self.parsed_items):
                    item_data = self.parsed_items[item_id]
                    # Si l'OID d'origine était déjà absolu et résolu, on le garde
                    # Sinon on recalcule par rapport à la base OID (sauf si c'est XXXX)
                    if item_data.get('resolved_oid', '').startswith(".") and ".1.3.6.1.4.1.XXXX" not in item_data.get('resolved_oid', ''):
                        full_oid = item_data['resolved_oid']
                    else:
                        full_oid = f"{base_oid}.{item_data['suffix']}.0"
                        
                    values = list(self.tree.item(item_id_str, "values"))
                    values[2] = full_oid
                    self.tree.item(item_id_str, values=values)
            except (ValueError, IndexError, UnboundLocalError):
                continue

    def filter_items(self, event=None):
        query = self.entry_search.get().lower()
        base_oid = self.entry_base_oid.get().strip()
        
        # Clear the tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Re-insert only matching items
        for item in self.parsed_items:
            if query in item['name'].lower() or query in item['desc'].lower():
                # On récupère l'OID actuellement affiché dans le treeview pour la cohérence
                # Ou on le recalcule si besoin (mieux vaut stocker l'OID actuel)
                full_oid = item.get('resolved_oid', f"{base_oid}.{item['suffix']}.0")
                checkbox = "☑" if item['selected'] else "☐"
                self.tree.insert("", "end", iid=item['id'], values=(checkbox, item['name'], full_oid, item['syntax'], item['desc']))

    def get_zabbix_type(self, syntax_str):
        s = syntax_str.lower()
        if "trap" in s:
            return "TEXT" # Traps are usually best as text/character
        if any(x in s for x in ["displaystring", "octet string", "string"]):
            return "CHAR"
        if any(x in s for x in ["integer", "counter", "gauge", "timeticks", "unsigned"]):
            return "FLOAT"
        return "TEXT"

    def generate_yaml(self):
        selected_items = [item for item in self.parsed_items if item['selected']]
        if not selected_items:
            messagebox.showwarning(self.t['msg_warn'], self.t['msg_no_selection'])
            return

        base_oid = self.entry_base_oid.get().strip()
        if base_oid and not base_oid.startswith("."):
            base_oid = "." + base_oid
            self.entry_base_oid.delete(0, tk.END)
            self.entry_base_oid.insert(0, base_oid)

        template_name = self.entry_tpl_name.get().strip()
        group_name = self.entry_group.get().strip()
        zabbix_version = self.entry_version.get().strip()
        default_delay = self.entry_delay.get().strip() or "8h"

        if "XXXX" in base_oid or base_oid == "":
            messagebox.showerror(self.t['msg_error'], self.t['msg_no_root'])
            return

        # Start Progress Bar
        self.progress_bar.pack(side="left", padx=20)
        self.btn_generate.configure(state="disabled")
        
        # Animate progress bar manually for visual effect
        def start_preview():
            for i in range(1, 101, 10):
                self.progress_bar.set(i / 100)
                self.update()
                time.sleep(0.05)
            
            # Prepare selected items data
            items_to_preview = selected_items

            # Reset UI before opening window to avoid stealing focus
            self.progress_bar.set(0)
            self.progress_bar.pack_forget()
            self.btn_generate.configure(state="normal")

            # Open Preview Window
            preview = PreviewWindow(self, items_to_preview, base_oid, template_name, group_name, zabbix_version, default_delay, lang=self.lang)
            
            # Force focus and lift
            preview.lift()
            preview.focus_force()
            preview.attributes("-topmost", True)
            preview.after(100, lambda: preview.attributes("-topmost", False)) # Keep it on top briefly

        # Delay opening slightly to let the animation show
        self.after(100, start_preview)

if __name__ == "__main__":
    app = MibToZabbixApp()
    app.mainloop()
