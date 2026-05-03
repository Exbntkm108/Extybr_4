import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import json
import os
import subprocess

class GitHubUserFinder:
    def __init__(self, master):
        self.master = master
        master.title("GitHub User Finder")

        self.favorites = self.load_favorites('favorites.json')

        # Поле ввода для поиска
        self.search_label = tk.Label(master, text="Введите имя пользователя GitHub:")
        self.search_label.pack()

        self.search_entry = tk.Entry(master, width=40)
        self.search_entry.pack()
        self.search_entry.bind("<Return>", self.search_user_event) # Поиск по нажатию Enter

        self.search_button = tk.Button(master, text="Найти", command=self.search_user)
        self.search_button.pack()

        # Область для отображения результатов
        self.results_label = tk.Label(master, text="Результаты поиска:")
        self.results_label.pack()

        self.results_text = scrolledtext.ScrolledText(master, width=50, height=10, wrap=tk.WORD)
        self.results_text.pack()

        # Кнопка добавления в избранное
        self.favorite_button = tk.Button(master, text="Добавить в избранное", command=self.add_to_favorites)
        self.favorite_button.pack()

        # Область для избранных пользователей
        self.favorites_label = tk.Label(master, text="Избранные пользователи:")
        self.favorites_label.pack()

        self.favorites_listbox = tk.Listbox(master, width=50, height=8)
        self.favorites_listbox.pack()
        self.update_favorites_listbox()

        self.load_favorites_button = tk.Button(master, text="Удалить из избранного", command=self.remove_from_favorites)
        self.load_favorites_button.pack()

    def load_favorites(self, filename='favorites.json'):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def save_favorites(self, filename='favorites.json'):
        with open(filename, 'w') as f:
            json.dump(self.favorites, f, indent=4)

    def search_user_event(self, event):
        self.search_user()

    def search_user(self):
        query = self.search_entry.get().strip()

        # Проверка корректности ввода
        if not query:
            messagebox.showwarning("Предупреждение", "Поле поиска не должно быть пустым.")
            return

        self.results_text.delete('1.0', tk.END)
        try:
            response = requests.get(f"https://api.github.com/search/users?q={query}")
            response.raise_for_status() # Вызовет исключение для плохих статусов (4xx или 5xx)
            data = response.json()

            if data['items']:
                for user in data['items']:
                    self.results_text.insert(tk.END, f"- {user['login']} (ID: {user['id']})\n")
            else:
                self.results_text.insert(tk.END, "Пользователи не найдены.\n")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить поиск: {e}")

    def add_to_favorites(self):
        selected_text = self.results_text.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        if not selected_text:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из списка результатов для добавления в избранное.")
            return

        parts = selected_text.split(" (ID: ")
        if len(parts) == 2:
            username = parts[0].lstrip('- ')
            user_id = int(parts[1].rstrip(')'))

            if username not in self.favorites:
                self.favorites.append({"login": username, "id": user_id})
                self.save_favorites()
                self.update_favorites_listbox()
            else:
                messagebox.showinfo("Информация", f"'{username}' уже находится в избранном.")
        else:
            messagebox.showwarning("Предупреждение", "Не удалось распознать пользователя для добавления в избранное.")

    def remove_from_favorites(self):
        selected_index = self.favorites_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из списка избранного для удаления.")
            return

        index = selected_index[0]
        del self.favorites[index]
        self.save_favorites()
        self.update_favorites_listbox()

    def update_favorites_listbox(self):
        self.favorites_listbox.delete(0, tk.END)
        for user in self.favorites:
            self.favorites_listbox.insert(tk.END, f"{user['login']} (ID: {user['id']})")

# Инициализация Git
def initialize_git_repo(repo_path="."):
    if not os.path.exists(os.path.join(repo_path, ".git")):
        subprocess.run(["git", "init"], cwd=repo_path)
        print("Git репозиторий создан.")
    else:
        print("Git репозиторий уже существует.")

def create_gitignore(repo_path="."):
    gitignore_path = os.path.join(repo_path, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write("__pycache__/\n")
            f.write("*.pyc\n")
            f.write("favorites.json\n") # Исключаем файл избранного из Git
        print(".gitignore создан.")
    else:
        print(".gitignore уже существует.")

if __name__ == "__main__":
    initialize_git_repo()
    create_gitignore()

    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
