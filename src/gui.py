import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from tkinter import messagebox, ttk
from models.model import criar_tabela, cadastrar_usuario, verificar_login
import crud

def abrir_login():
    janela_inicial.withdraw()
    login = ctk.CTkToplevel()
    login.title("Login")
    login.geometry("350x250")
    login.transient(janela_inicial)
    login.resizable(False, False)
    frame = ctk.CTkFrame(login)
    frame.pack(expand=True)
    ctk.CTkLabel(frame, text="Usuário:", font=("Arial", 14)).pack(pady=(20, 5))
    entrada_usuario = ctk.CTkEntry(frame, width=200)
    entrada_usuario.pack(pady=5)
    ctk.CTkLabel(frame, text="Senha:", font=("Arial", 14)).pack(pady=5)
    entrada_senha = ctk.CTkEntry(frame, show="*", width=200)
    entrada_senha.pack(pady=5)
    def tentar_login():
        usuario = entrada_usuario.get()
        senha = entrada_senha.get()
        if verificar_login(usuario, senha):
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            login.destroy()
            abrir_pagina_inicial(usuario)
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos")
    ctk.CTkButton(frame, text="Entrar", command=tentar_login).pack(pady=20)
    def fechar_login():
        login.destroy()
        janela_inicial.deiconify()
    login.protocol("WM_DELETE_WINDOW", fechar_login)

def abrir_registro():
    janela_inicial.withdraw()
    registro = ctk.CTkToplevel()
    registro.title("Registro de Usuário")
    registro.geometry("350x300")
    registro.transient(janela_inicial)
    registro.resizable(False, False)
    frame = ctk.CTkFrame(registro)
    frame.pack(expand=True)
    ctk.CTkLabel(frame, text="Novo Usuário:", font=("Arial", 14)).pack(pady=(20, 5))
    entrada_novo_usuario = ctk.CTkEntry(frame, width=200)
    entrada_novo_usuario.pack(pady=5)
    ctk.CTkLabel(frame, text="Nova Senha:", font=("Arial", 14)).pack(pady=5)
    entrada_nova_senha = ctk.CTkEntry(frame, show="*", width=200)
    entrada_nova_senha.pack(pady=5)
    ctk.CTkLabel(frame, text="Confirme a Senha:", font=("Arial", 14)).pack(pady=5)
    entrada_confirma_senha = ctk.CTkEntry(frame, show="*", width=200)
    entrada_confirma_senha.pack(pady=5)
    def tentar_registro():
        usuario, senha, confirma = entrada_novo_usuario.get(), entrada_nova_senha.get(), entrada_confirma_senha.get()
        if not usuario or not senha: messagebox.showerror("Erro", "Usuário e senha vazios."); return
        if senha != confirma: messagebox.showerror("Erro", "Senhas não coincidem."); return
        if cadastrar_usuario(usuario, senha):
            messagebox.showinfo("Sucesso", f"Usuário {usuario} registrado!")
            registro.destroy(); janela_inicial.deiconify()
        else:
            messagebox.showerror("Erro", "Usuário já existe.")
    ctk.CTkButton(frame, text="Registrar", command=tentar_registro).pack(pady=20)
    def fechar_registro():
        registro.destroy(); janela_inicial.deiconify()
    registro.protocol("WM_DELETE_WINDOW", fechar_registro)

def abrir_janela_grafico(data, uf, parent_window):
    janela_grafico = ctk.CTkToplevel()
    janela_grafico.title(f"Gráfico - {uf}")
    janela_grafico.geometry("900x700")
    janela_grafico.transient(parent_window)
    janela_grafico.grab_set()

    chart_data = {k.replace('_', ' ').title(): v for k, v in data.items() if isinstance(v, (int, float))}
    if not chart_data:
        ctk.CTkLabel(janela_grafico, text="Não há dados para exibir.").pack(expand=True)
        return

    fig, ax = plt.subplots(facecolor='#FFFFFF')
    labels = list(chart_data.keys())
    values = list(chart_data.values())
    colors = plt.cm.viridis(np.linspace(0, 1, len(values)))
    
    bars = ax.barh(labels, values, color=colors)
    ax.set_xlabel('Valores')
    ax.set_title(f'Dados para {uf}')
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width * 1.01, bar.get_y() + bar.get_height()/2, f'{width:,.2f}', ha='left', va='center', fontsize=9)
    
    fig.tight_layout(pad=3.0)
    
    canvas = FigureCanvasTkAgg(fig, master=janela_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(side='top', fill='both', expand=True, padx=10, pady=10)

def abrir_pagina_inicial(nome_usuario):
    pagina = ctk.CTkToplevel()
    pagina.title("Dashboard IBGE")
    pagina.geometry("1100x750")

    ctk.CTkLabel(pagina, text=f"Bem-vindo, {nome_usuario}!", font=("Arial", 20, "bold")).pack(pady=10)

    tabview = ctk.CTkTabview(pagina, width=1050, height=650)
    tabview.pack(pady=10, expand=True, fill='both', padx=20)
    
    tab_resumo = tabview.add("Resumo Geral")
    tab_estado = tabview.add("Análise por Estado")
    tab_insights = tabview.add("Insights & Rankings")

    frame_resumo_geral = ctk.CTkFrame(tab_resumo, fg_color="transparent")
    frame_resumo_geral.pack(pady=10, padx=10, fill="both", expand=True)
    ctk.CTkLabel(frame_resumo_geral, text="População por Estado", font=("Arial", 16, "bold")).pack(pady=10)
    style = ttk.Style(); style.theme_use("default")
    style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=25, fieldbackground="#343638", bordercolor="#343638", borderwidth=0)
    style.map('Treeview', background=[('selected', '#22559b')]); style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
    style.map("Treeview.Heading", background=[('active', '#3484F0')])
    tabela_frame = ctk.CTkFrame(frame_resumo_geral, fg_color="transparent")
    tabela_frame.pack(pady=10, fill='both', expand=True)
    colunas = ['UF', 'População']; tabela = ttk.Treeview(tabela_frame, columns=colunas, show='headings')
    tabela.heading('UF', text='UF'); tabela.heading('População', text='População')
    tabela.column('UF', width=150, anchor='center'); tabela.column('População', width=200, anchor='center')
    tabela.pack(fill='both', expand=True)
    def mostrar_populacao_uf():
        dados = crud.get_population_by_uf()
        tabela.delete(*tabela.get_children())
        if dados:
            for item in dados: tabela.insert('', 'end', values=(item['sigla_uf'], f"{int(item['populacao']):,}"))
        else: messagebox.showerror("Erro", "Não foi possível carregar os dados.")
    ctk.CTkButton(frame_resumo_geral, text="Carregar Dados", command=mostrar_populacao_uf).pack(pady=20)

    frame_analise_estado = ctk.CTkFrame(tab_estado, fg_color="transparent")
    frame_analise_estado.pack(fill="both", expand=True)
    
    top_frame = ctk.CTkFrame(frame_analise_estado, fg_color="transparent")
    top_frame.pack(fill='x', pady=5, padx=10)
    ctk.CTkLabel(top_frame, text="Selecione a UF:", font=("Arial", 14)).pack(side='left', padx=(0, 10))
    lista_ufs = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
    uf_var = ctk.StringVar()
    combobox_uf = ctk.CTkComboBox(top_frame, variable=uf_var, values=lista_ufs, state='readonly', width=100)
    combobox_uf.pack(side='left', padx=10)
    
    scroll_frame = ctk.CTkScrollableFrame(frame_analise_estado, fg_color="transparent")
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
    resultado_texto = ctk.CTkTextbox(scroll_frame, height=200, font=("Arial", 12))
    resultado_texto.pack(pady=10, fill='x', padx=10)
    form_frame = ctk.CTkFrame(scroll_frame)
    form_frame.pack(pady=10, padx=10, fill='x')
    
    ctk.CTkLabel(form_frame, text="Editar Dados do Estado", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10, padx=10)
    labels = ['População', 'Área', 'Domicílios', 'Pop. Indígena', 'Pop. Quilombola', 'Taxa Alfabetização', 'Idade Mediana', 'Índice Envelhecimento', 'Razão do Sexo']
    api_keys = ['populacao', 'area', 'domicilios', 'populacao_indigena', 'populacao_quilombola', 'taxa_alfabetizacao', 'idade_mediana', 'indice_envelhecimento', 'razao_sexo']
    entries = {}
    for i, label_text in enumerate(labels):
        ctk.CTkLabel(form_frame, text=label_text+":").grid(row=i+1, column=0, padx=10, pady=5, sticky='e')
        entry = ctk.CTkEntry(form_frame, width=200)
        entry.grid(row=i+1, column=1, padx=10, pady=5, sticky='w')
        entries[api_keys[i]] = entry
    botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    botoes_frame.grid(row=len(labels)+1, column=0, columnspan=2, pady=15)
    
    def buscar_e_mostrar_dados(uf):
        if not uf: messagebox.showerror("Erro", "Selecione uma UF."); return
        dados = crud.get_by_uf(uf)
        resultado_texto.delete("1.0", "end")
        if dados and 'error' not in dados:
            for key, value in dados.items():
                label = key.replace('_', ' ').title()
                display_value = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
                resultado_texto.insert("end", f"{label}: {display_value}\n")
            abrir_janela_grafico(dados, uf, pagina)
        else:
            resultado_texto.insert("end", f"Nenhum dado para {uf}.");
    
    ctk.CTkButton(top_frame, text="Pesquisar", command=lambda: buscar_e_mostrar_dados(uf_var.get())).pack(side='left', padx=10)
    
    def limpar_campos():
        uf_var.set(''); resultado_texto.delete("1.0", "end")
        for entry in entries.values(): entry.delete(0, 'end')
    def preencher_form(uf):
        if not uf: messagebox.showerror("Erro", "Selecione uma UF."); return
        dados = crud.get_by_uf(uf)
        if dados and 'error' not in dados:
            for key, entry_widget in entries.items():
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, dados.get(key, ''))
        else:
            messagebox.showerror("Erro", f"Dados para {uf} não encontrados."); limpar_campos()
    def salvar_edicao(uf):
        if not uf: messagebox.showerror("Erro", "Selecione uma UF."); return
        try:
            data = {key: float(entry.get()) for key, entry in entries.items() if entry.get()}
            if not data: messagebox.showwarning("Aviso", "Nenhum dado alterado."); return
            if crud.update_uf(uf, data):
                messagebox.showinfo("Sucesso", f"Dados de {uf} atualizados!")
                buscar_e_mostrar_dados(uf)
            else: messagebox.showerror("Erro", f"Falha ao atualizar.")
        except ValueError: messagebox.showerror("Erro", "Insira apenas números.")
    def deletar_uf(uf):
        if not uf: messagebox.showerror("Erro", "Selecione uma UF."); return
        if messagebox.askyesno("Confirmação", f"Deletar dados de {uf}?"):
            if crud.delete_uf(uf):
                messagebox.showinfo("Sucesso", f"Dados de {uf} deletados."); limpar_campos()
            else: messagebox.showerror("Erro", f"Falha ao deletar.")
    ctk.CTkButton(botoes_frame, text="Preencher Formulário", command=lambda: preencher_form(uf_var.get())).pack(side='left', padx=10)
    ctk.CTkButton(botoes_frame, text="Salvar Alterações", command=lambda: salvar_edicao(uf_var.get())).pack(side='left', padx=10)
    ctk.CTkButton(botoes_frame, text="Deletar Estado", fg_color="#D32F2F", hover_color="#B71C1C", command=lambda: deletar_uf(uf_var.get())).pack(side='left', padx=10)
    

    insights_main_frame = ctk.CTkFrame(tab_insights, fg_color="transparent")
    insights_main_frame.pack(fill='both', expand=True)

    ctk.CTkButton(insights_main_frame, text="Gerar Análises Gráficas", 
                  command=lambda: carregar_insights_graficos()).pack(pady=10)
    
    scrollable_charts_area = ctk.CTkScrollableFrame(insights_main_frame, fg_color="transparent")
    scrollable_charts_area.pack(fill='both', expand=True, padx=5, pady=5)

    def carregar_insights_graficos():
        for widget in scrollable_charts_area.winfo_children():
            widget.destroy()

        dados = crud.get_rankings()
        if not dados:
            messagebox.showerror("Erro", "Não foi possível carregar os insights."); return
        
        explicacao_pop = (
            "Definição:\n"
            "Representa a proporção da população dos cinco estados mais populosos em relação ao restante do Brasil.\n"
            "A fatia 'Outros' agrupa a população de todos os demais estados e do Distrito Federal.\n\n"
            "Método de Cálculo:\n"
            "1. O sistema soma a `populacao` de todos os municípios para obter o total de cada estado.\n"
            "2. Identifica os 5 estados com os maiores totais de população.\n"
            "3. A fatia 'Outros' é calculada subtraindo a soma da população desses 5 estados da população total do Brasil.\n"
            "4. O gráfico de pizza mostra a proporção de cada um desses grupos (Top 5 + Outros)."
        )
        label_pop = ctk.CTkLabel(scrollable_charts_area, text=explicacao_pop, justify="left", wraplength=900, font=("Arial", 12))
        label_pop.pack(fill="x", padx=10, pady=(10, 5))

        pop_data = dados.get('populacao_top5', {})
        pop_total = dados.get('populacao_total', 0)
        soma_top5 = sum(pop_data.values())
        outros = pop_total - soma_top5
        pop_labels = list(pop_data.keys()) + ['Outros']
        pop_values = list(pop_data.values()) + [outros]
        
        fig_pop, ax_pop = plt.subplots(facecolor='#2b2b2b')
        wedges, texts, autotexts = ax_pop.pie(pop_values, labels=pop_labels, autopct='%1.1f%%', startangle=140, textprops={'color':"w"})
        ax_pop.axis('equal'); ax_pop.set_title('Distribuição da População (Top 5)', color='white')
        plt.setp(autotexts, color='black', weight='bold')

        canvas_pop = FigureCanvasTkAgg(fig_pop, master=scrollable_charts_area)
        canvas_pop.get_tk_widget().pack(fill="x", padx=10, pady=10)

        explicacao_alf = (
            "Definição:\n"
            "A Taxa de Alfabetização é o percentual de pessoas com 15 anos ou mais que sabem ler e escrever.\n"
            "É um indicador fundamental do capital humano de uma região.\n\n"
            "Método de Cálculo:\n"
            "1. O sistema utiliza a coluna `taxa_alfabetizacao` do arquivo CSV, que já existe para cada município.\n"
            "2. Para obter o valor de um estado, o sistema calcula a média aritmética de todas as taxas dos municípios daquele estado.\n"
            "3. O gráfico de barras exibe os 5 estados com as maiores médias, permitindo uma comparação direta."
        )
        label_alf = ctk.CTkLabel(scrollable_charts_area, text=explicacao_alf, justify="left", wraplength=900, font=("Arial", 12))
        label_alf.pack(fill="x", padx=10, pady=(20, 5))
        
        alf_data = dados.get('alfabetizacao_top5', {})
        fig_alf, ax_alf = plt.subplots(facecolor='#2b2b2b', figsize=(10, 4))
        ax_alf.barh(list(alf_data.keys()), list(alf_data.values()), color='skyblue')
        ax_alf.set_title('Top 5 - Maiores Taxas de Alfabetização (%)', color='white')
        ax_alf.set_facecolor("#2b2b2b"); ax_alf.tick_params(colors='white')
        fig_alf.tight_layout()

        canvas_alf = FigureCanvasTkAgg(fig_alf, master=scrollable_charts_area)
        canvas_alf.get_tk_widget().pack(fill="x", padx=10, pady=10)
        
        explicacao_env = (
            "Definição:\n"
            "O Índice de Envelhecimento indica quantas pessoas de 60 anos ou mais existem para cada 100 jovens de até 14 anos.\n"
            "Um índice alto sugere uma estrutura populacional mais envelhecida.\n\n"
            "Método de Cálculo:\n"
            "1. O sistema usa a coluna `indice_envelhecimento` do arquivo CSV, disponível para cada município.\n"
            "2. O índice de um estado é calculado através da média aritmética dos índices de todos os seus municípios.\n"
            "3. O gráfico mostra os 5 estados com as maiores médias."
        )
        label_env = ctk.CTkLabel(scrollable_charts_area, text=explicacao_env, justify="left", wraplength=900, font=("Arial", 12))
        label_env.pack(fill="x", padx=10, pady=(20, 5))

        env_data = dados.get('envelhecimento_top5', {})
        fig_env, ax_env = plt.subplots(facecolor='#2b2b2b', figsize=(10, 4))
        ax_env.barh(list(env_data.keys()), list(env_data.values()), color='salmon')
        ax_env.set_title('Top 5 - Maiores Índices de Envelhecimento', color='white')
        ax_env.set_facecolor("#2b2b2b"); ax_env.tick_params(colors='white')
        fig_env.tight_layout()

        canvas_env = FigureCanvasTkAgg(fig_env, master=scrollable_charts_area)
        canvas_env.get_tk_widget().pack(fill="x", padx=10, pady=10)

    def sair():
        pagina.destroy(); janela_inicial.deiconify()
    ctk.CTkButton(pagina, text="Sair e Voltar", command=sair, fg_color="#555555", hover_color="#444444").pack(pady=20, side="bottom")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    criar_tabela()
    janela_inicial = ctk.CTk()
    janela_inicial.title("Tela Inicial")
    janela_inicial.geometry("400x200")
    janela_inicial.resizable(False, False)
    frame_central = ctk.CTkFrame(janela_inicial)
    frame_central.pack(expand=True)
    ctk.CTkLabel(frame_central, text="Bem-vindo!", font=("Arial", 18, "bold")).pack(pady=20)
    frame_botoes = ctk.CTkFrame(frame_central, fg_color="transparent")
    frame_botoes.pack(pady=20, fill="x", expand=True)
    btn_login = ctk.CTkButton(frame_botoes, text="Login", width=120, height=40, command=abrir_login)
    btn_login.pack(side='left', expand=True, padx=10)
    btn_registrar = ctk.CTkButton(frame_botoes, text="Registrar", width=120, height=40, command=abrir_registro)
    btn_registrar.pack(side='right', expand=True, padx=10)
    janela_inicial.mainloop()