import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import uuid
import yaml
import os
import time
from collections import Counter

APP_VERSION = "1.0.0"

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
        "placeholder_group": "Templates/Network Devices",
        "lbl_base_oid": "OID Racine (Base) :",
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
        "placeholder_group": "Templates/Network Devices",
        "lbl_base_oid": "Root OID (Base):",
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
    def __init__(self, parent, selected_items, base_oid, template_name, group_name, zabbix_version, lang="FR"):
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
            full_oid = f"{self.base_oid}.{item['suffix']}.0"
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
            key_entry.insert(0, f"snmp.{item['name'].lower()}")
            
            # Description
            ctk.CTkLabel(frame, text=self.t['lbl_desc']).grid(row=2, column=0, padx=5, pady=5, sticky="e")
            desc_entry = ctk.CTkEntry(frame, width=300)
            desc_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
            desc_entry.insert(0, item['desc'])

            # Tags (New)
            ctk.CTkLabel(frame, text=self.t['lbl_tags']).grid(row=2, column=2, padx=5, pady=5, sticky="e")
            tags_entry = ctk.CTkEntry(frame, width=300, placeholder_text="component:mib-import, device:snmp")
            tags_entry.grid(row=2, column=3, padx=5, pady=5, sticky="w")
            tags_entry.insert(0, "component:mib-import")
            
            self.item_widgets.append({
                "item_id": item['id'],
                "suffix": item['suffix'],
                "syntax": item['syntax'],
                "name_entry": name_entry,
                "key_entry": key_entry,
                "desc_entry": desc_entry,
                "tags_entry": tags_entry
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
            
            full_oid = f"{self.base_oid}.{w['suffix']}.0"
            
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
                "type": "SNMP_AGENT",
                "snmp_oid": full_oid,
                "key": key,
                "delay": "1m",
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

        file_path = filedialog.asksaveasfilename(defaultextension=".yaml", filetypes=[("YAML files", "*.yaml")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(zbx_template, f, sort_keys=False, allow_unicode=True)
            
            messagebox.showinfo(self.t['msg_success'], self.t['msg_saved'])
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

        columns = ("name", "oid", "syntax", "desc")
        self.tree = ttk.Treeview(self.tree_container, columns=columns, show='headings', selectmode="extended")
        
        self.tree.heading("name", text=self.t['col_name'])
        self.tree.heading("oid", text=self.t['col_oid'])
        self.tree.heading("syntax", text=self.t['col_syntax'])
        self.tree.heading("desc", text=self.t['col_desc'])
        
        self.tree.column("name", width=250)
        self.tree.column("oid", width=250)
        self.tree.column("syntax", width=150)
        self.tree.column("desc", width=600)

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
        self.label_oid.configure(text=self.t['lbl_base_oid'])
        self.lbl_help.configure(text=self.t['lbl_help_oid'])
        
        # List Frame
        self.list_header.configure(text=self.t['list_header'])
        self.entry_search.configure(placeholder_text=self.t['search_placeholder'])
        self.lbl_search.configure(text=self.t['search_label'])
        
        # Treeview
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

        # --- Détection Robuste de l'OID Racine ---
        # 1. Dictionnaire des identifiants OID connus
        known_oids = {
            "iso": "1",
            "org": "1.3",
            "dod": "1.3.6",
            "internet": "1.3.6.1",
            "directory": "1.3.6.1.1",
            "mgmt": "1.3.6.1.2",
            "mib-2": "1.3.6.1.2.1",
            "transmission": "1.3.6.1.2.1.10",
            "experimental": "1.3.6.1.3",
            "private": "1.3.6.1.4",
            "enterprises": "1.3.6.1.4.1",
            "security": "1.3.6.1.5",
            "snmpv2": "1.3.6.1.6",
            "snmpModules": "1.3.6.1.6.3",
        }

        # 2. Extraire tous les OBJECT IDENTIFIER et MODULE-IDENTITY
        # Format: nom OBJECT IDENTIFIER ::= { parent 123 } ou { 1 2 3 }
        id_pattern = re.compile(r'(\w+)\s+(?:OBJECT IDENTIFIER|MODULE-IDENTITY).*?::=\s+\{\s*(.*?)\s*\}', re.DOTALL | re.IGNORECASE)
        found_ids = id_pattern.findall(self.mib_content)
        
        # On fait plusieurs passes pour résoudre les dépendances
        for _ in range(5):
            for name, content in found_ids:
                parts = content.split()
                if not parts: continue
                
                # Cas 1: { 1 2 3 } (full numeric)
                if parts[0].isdigit():
                    known_oids[name] = ".".join(parts)
                # Cas 2: { parent 123 }
                elif parts[0] in known_oids:
                    parent_val = known_oids[parts[0]]
                    suffix = ".".join(parts[1:])
                    known_oids[name] = f"{parent_val}.{suffix}"

        # 3. Trouver le point de départ le plus probable pour le template
        # On cherche l'OID le plus long qui n'est pas un OBJECT-TYPE
        # Mais on privilégie ceux qui sont "parents" dans le fichier
        suggested_root = "1.3.6.1.4.1.XXXX"
        
        # On récupère tous les parents cités dans les OBJECT-TYPE ::= { PARENT suffix }
        parent_usage_pattern = re.compile(r'::=\s+\{\s*([\w\d\-]+)\s+\d+\s*\}')
        all_parents = parent_usage_pattern.findall(self.mib_content)
        
        if all_parents:
            # On prend le parent le plus fréquent qui est dans known_oids
            from collections import Counter
            most_common_parent = Counter(all_parents).most_common(1)[0][0]
            if most_common_parent in known_oids:
                suggested_root = known_oids[most_common_parent]

        # Si toujours pas trouvé, on tente de trouver au moins une racine d'entreprise
        if "XXXX" in suggested_root:
            for name, val in known_oids.items():
                if val.startswith("1.3.6.1.4.1.") and len(val.split('.')) > 6:
                    suggested_root = val
                    break

        self.entry_base_oid.delete(0, tk.END)
        self.entry_base_oid.insert(0, suggested_root)
        if "XXXX" not in suggested_root:
            self.lbl_help.configure(text=f"({self.t['lbl_detected_root']} {suggested_root})", text_color="#28a745")
        else:
            self.lbl_help.configure(text=f"({self.t['lbl_no_root']})", text_color="#3b8ed0")

        # --- Fin Détection ---
        pattern = re.compile(
            r'(\w+)\s+OBJECT-TYPE\s+.*?'
            r'SYNTAX\s+(.*?)\s+(?:MAX-ACCESS|ACCESS)\s+.*?'
            r'DESCRIPTION\s+"(.*?)"\s+.*?'
            r'::=\s+\{\s*[\w\d\-]+\s+(\d+)\s*\}',
            re.DOTALL | re.IGNORECASE
        )

        matches = pattern.findall(self.mib_content)
        
        if not matches:
            messagebox.showwarning(self.t['msg_warn'], "Aucun objet 'OBJECT-TYPE' standard trouvé / No standard objects found.")
            return

        count = 0
        base_oid = self.entry_base_oid.get().strip()
        for name, syntax, desc, suffix in matches:
            desc_clean = " ".join(desc.split())
            syntax_clean = syntax.strip()
            
            if "SEQUENCE" in syntax_clean:
                continue

            full_oid = f"{base_oid}.{suffix}.0"
            self.tree.insert("", "end", iid=count, values=(name, full_oid, syntax_clean, desc_clean))
            self.parsed_items.append({
                "id": count,
                "name": name,
                "suffix": suffix,
                "syntax": syntax_clean,
                "desc": desc_clean
            })
            count += 1
            
        messagebox.showinfo(self.t['msg_success'], f"{count} {self.t['msg_mib_success']}")

    def select_all(self):
        children = self.tree.get_children()
        self.tree.selection_set(children)

    def update_oids(self, event=None):
        base_oid = self.entry_base_oid.get().strip()
        for item_id_str in self.tree.get_children():
            try:
                item_id = int(item_id_str)
                if item_id < len(self.parsed_items):
                    suffix = self.parsed_items[item_id]['suffix']
                    full_oid = f"{base_oid}.{suffix}.0"
                    values = list(self.tree.item(item_id_str, "values"))
                    values[1] = full_oid
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
                full_oid = f"{base_oid}.{item['suffix']}.0"
                self.tree.insert("", "end", iid=item['id'], values=(item['name'], full_oid, item['syntax'], item['desc']))

    def get_zabbix_type(self, syntax_str):
        s = syntax_str.lower()
        if any(x in s for x in ["displaystring", "octet string", "string"]):
            return "CHAR"
        if any(x in s for x in ["integer", "counter", "gauge", "timeticks", "unsigned"]):
            return "FLOAT"
        return "TEXT"

    def generate_yaml(self):
        selected_ids = self.tree.selection()
        if not selected_ids:
            messagebox.showwarning(self.t['msg_warn'], self.t['msg_no_selection'])
            return

        base_oid = self.entry_base_oid.get().strip()
        template_name = self.entry_tpl_name.get().strip()
        group_name = self.entry_group.get().strip()
        zabbix_version = self.entry_version.get().strip()

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
            items_to_preview = []
            for iid in selected_ids:
                items_to_preview.append(self.parsed_items[int(iid)])

            # Open Preview Window
            preview = PreviewWindow(self, items_to_preview, base_oid, template_name, group_name, zabbix_version, lang=self.lang)
            preview.focus()
            
            # Reset UI
            self.progress_bar.set(0)
            self.progress_bar.pack_forget()
            self.btn_generate.configure(state="normal")

        # Delay opening slightly to let the animation show
        self.after(100, start_preview)

if __name__ == "__main__":
    app = MibToZabbixApp()
    app.mainloop()
