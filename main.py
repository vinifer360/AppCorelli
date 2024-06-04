from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials, auth
import requests
from datetime import datetime
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import MDList, OneLineListItem, ThreeLineListItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown

cred = credentials.Certificate(r"C:\Users\Vinicius Fernandes\PycharmProjects\pythonProject4\aplicativocorelli-firebase-adminsdk-ko8uz-02f0215ad4.json")
firebase_admin.initialize_app(cred)

class AcessoInvalidoPopup(Popup):
    def __init__(self, **kwargs):
        super(AcessoInvalidoPopup, self).__init__(**kwargs)
        self.title = 'Acesso Inválido'
        self.size_hint = (None, None)
        self.size = (200, 100)
        self.auto_dismiss = False

        content = Button(text='Acesso Inválido')
        content.bind(on_press=self.dismiss)
        self.add_widget(content)

class LoginScreen(Screen):
    def login(self):
        email = self.ids.email.text
        self.authenticate(email)

    def authenticate(self, email):
        try:
            user = auth.get_user_by_email(email)
            self.manager.current = 'tela_principal'  # Navegar para a próxima tela
        except auth.UserNotFoundError:
            print("Usuário não encontrado")
            AcessoInvalidoPopup().open()
        except Exception as e:
            print(f"Erro durante a autenticação: {e}")

class TelaPrincipal(Screen):
    def goto_SolicitarColeta(self):
        self.manager.current = "solicitar_coleta"

    def goto_BaixarEntregas(self):
        self.manager.current = "baixar_entregas"

    def goto_VerStatus(self):
        self.manager.current = "ver_coletas"

class VerStatus(Screen):
    def goto_coletaspedidas(self):
        self.manager.current = "coletas_pedidas"

    def goto_entregasfeitas(self):
        self.manager.current = "entregas_feitas"


class SenhaMasterPopup(Popup):
    def __init__(self, on_confirm, on_cancel, **kwargs):
        super(SenhaMasterPopup, self).__init__(**kwargs)
        self.title = "Senha Master"
        self.size_hint = (None, None)
        self.size = (200, 150)

        layout = BoxLayout(orientation='vertical')

        self.password_input = TextInput(hint_text="Digite a Senha", password=True)
        layout.add_widget(self.password_input)

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=10)
        button_layout.add_widget(Button(text="Confirmar", on_press=on_confirm))
        button_layout.add_widget(Button(text="Cancelar", on_press=on_cancel))
        layout.add_widget(button_layout)

        self.content = layout

    def get_password(self):
        return self.password_input.text


class ColetasPedidas(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_action = ""

    def on_enter(self):
        self.carregar_solicitacoes()

    def carregar_solicitacoes(self, data=None, usuario=None):
        db = firestore.client()
        coletas_ref = db.collection('Coletas_Solicitadas').get()

        self.ids.lista_coletas.clear_widgets()

        for coleta in coletas_ref:
            dados = coleta.to_dict()
            if (not data or data in dados['data']) and \
                    (not usuario or usuario in dados['motorista']):
                item = ThreeLineListItem(
                    text=f"Item: {dados['item']} - Data: {dados['data']} - Horário: {dados['hora']}",
                    secondary_text=f"No endereço: {dados['rua']}, {dados['numero']}",
                    tertiary_text=f" {dados['complemento']} - CEP: {dados['cep']} - Courier: {dados.get('motorista')}",
                    font_style="Caption",
                    secondary_font_style="Overline",
                    tertiary_font_style="Overline"
                )
                item.bind(on_release=lambda x, coleta_id=coleta.id: self.solicitar_senha(coleta_id))
                self.ids.lista_coletas.add_widget(item)

    def aplicar_filtros(self):
        data = self.ids.filtro_data.text
        usuario = self.ids.filtro_courier.text
        self.atualizar_lista(data, usuario)

    def atualizar_lista(self, data, usuario):
        db = firestore.client()
        coletas_ref = db.collection('Coletas_Solicitadas').get()

        self.ids.lista_coletas.clear_widgets()

        for coleta in coletas_ref:
            dados = coleta.to_dict()
            if (not data or data in dados['data']) and \
                    (not usuario or usuario in dados['motorista']):
                item = ThreeLineListItem(
                    text=f"Item: {dados['item']} - Data: {dados['data']} - Horário: {dados['hora']}",
                    secondary_text=f"No endereço: {dados['rua']}, {dados['numero']}",
                    tertiary_text=f" {dados['complemento']} - CEP: {dados['cep']} - Courier: {dados.get('motorista')}",
                    font_style="Caption",
                    secondary_font_style="Overline",
                    tertiary_font_style="Overline"
                )
                item.bind(on_release=lambda x, coleta_id=coleta.id: self.solicitar_senha(coleta_id))
                self.ids.lista_coletas.add_widget(item)

    def solicitar_senha(self, coleta_id):
        self.coleta_id = coleta_id

        password_layout = BoxLayout(orientation='vertical')
        password_input = TextInput(password=True, multiline=False)
        buttons_layout = BoxLayout(size_hint_y=None, height=50)
        confirm_button = Button(text='Confirmar', on_release=self.validar_senha)
        cancel_button = Button(text='Cancelar', on_release=self.cancelar_acao)

        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)
        password_layout.add_widget(password_input)
        password_layout.add_widget(buttons_layout)

        self.password_popup = Popup(title='Digite a senha', content=password_layout, size_hint=(None, None), size=(400, 200))
        self.password_input = password_input
        self.password_popup.open()

    def validar_senha(self, instance):
        if self.password_input.text == "teste":
            self.password_popup.dismiss()
            self.exibir_opcoes()
        else:
            self.password_input.text = ""
            self.exibir_mensagem_erro()

    def cancelar_acao(self, instance):
        self.password_popup.dismiss()

    def exibir_opcoes(self):
        opcoes_layout = BoxLayout(orientation='vertical')
        motorista_button = Button(text='Exibir seleção de motorista', size_hint_y=None, height=50, on_release=self.selecao_motorista_acao)
        realizada_button = Button(text='Marcar como realizada', size_hint_y=None, height=50, on_release=self.realizar_acao)

        opcoes_layout.add_widget(motorista_button)
        opcoes_layout.add_widget(realizada_button)

        self.opcoes_popup = Popup(title='Opções de Coleta', content=opcoes_layout, size_hint=(None, None), size=(400, 200))
        self.opcoes_popup.open()

    def selecao_motorista_acao(self, instance):
        self.opcoes_popup.dismiss()
        self.exibir_selecao_motorista(self.coleta_id)

    def realizar_acao(self, instance):
        self.opcoes_popup.dismiss()
        self.marcar_coleta_realizada(self.coleta_id)

    def exibir_selecao_motorista(self, coleta_id):
        db = firestore.client()
        couriers_ref = db.collection('Couriers').get()

        popup_layout = BoxLayout(orientation='vertical')
        popup = Popup(title='Selecione um motorista', content=popup_layout, size_hint=(None, None), size=(350, 400))

        for courier in couriers_ref:
            nome_motorista = courier.get('Nome')
            btn = Button(text=nome_motorista, size_hint_y=None, height=30)
            btn.bind(on_release=lambda btn, nome=nome_motorista: self.distribuir_coleta_para_motorista(coleta_id, nome))
            popup_layout.add_widget(btn)

        popup.open()

    def marcar_coleta_realizada(self, coleta_id):
        db = firestore.client()

        # Obtenha a referência da coleta
        coleta_ref = db.collection('Coletas_Solicitadas').document(coleta_id)

        # Obtenha os dados da coleta
        coleta = coleta_ref.get().to_dict()

        coleta['data_realizacao'] = datetime.now().strftime("%d/%m/%Y")
        coleta['hora_realizacao'] = datetime.now().strftime("%H:%M")

        # Adicione a coleta à coleção de Coletas_Realizadas
        db.collection('Coletas_Realizadas').add(coleta)

        # Remova a coleta da coleção de Coletas_Solicitadas
        coleta_ref.delete()

        # Atualize a lista de coletas solicitadas
        self.carregar_solicitacoes()

    def exibir_mensagem_erro(self):
        error_popup = Popup(title='Erro', content=Label(text='Senha incorreta!'), size_hint=(None, None), size=(400, 200))
        error_popup.open()

    def distribuir_coleta_para_motorista(self, coleta_id, nome_motorista):
        db = firestore.client()
        coleta_ref = db.collection('Coletas_Solicitadas').document(coleta_id)
        coleta_ref.update({'motorista': nome_motorista})

        self.carregar_solicitacoes()

    def voltar_ver_status(self):
        self.manager.current = "ver_coletas"

class EntregasFeitas(Screen):
    def on_enter(self):
        self.carregar_coletas_realizadas()

    def carregar_coletas_realizadas(self):
        db = firestore.client()
        coletas_realizadas_ref = db.collection('Coletas_Realizadas').get()

        self.ids.lista_coletas_realizadas.clear_widgets()

        for coleta in coletas_realizadas_ref:
            dados = coleta.to_dict()
            item = ThreeLineListItem(
                text=f"Item: {dados['item']} - Data: {dados['data_realizacao']} - Horário: {dados['hora_realizacao']}",
                secondary_text=f"No endereço: {dados['rua']}, {dados['numero']} - {dados['complemento']} - CEP: {dados['cep']}",
                tertiary_text=f"Courier: {dados.get('motorista')}"
            )
            self.ids.lista_coletas_realizadas.add_widget(item)

class SolicitarColeta(Screen):
    data_selecionada = None
    hora_selecionada = None
    dialog = None

    def preencher_endereco(self):
        cep = self.ids.cep_field.text
        if len(cep) == 8:
            try:
                response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
                if response.status_code == 200:
                    endereco = response.json()
                    self.ids.rua_field.text = endereco.get("logradouro", "")
                    self.ids.numero_field.text = ""
                    self.ids.bairro_field.text = endereco.get("bairro", "")
                    self.ids.cidade_field.text = endereco.get("localidade", "")
                    self.ids.cep_field.text = endereco.get("cep", "")
            except requests.RequestException as e:
                print(f"Erro ao acessar a API do ViaCEP: {e}")

    def selecionar_data(self):
        picker = MDDatePicker()
        picker.bind(on_save=self.definir_data)
        picker.open()

    def definir_data(self, instance, value, date_range):
        self.data_selecionada = value

    def selecionar_hora(self):
        picker = MDTimePicker()
        picker.bind(time=self.definir_hora)
        picker.open()

    def definir_hora(self, picker_widget, hora):
        self.hora_selecionada = hora

    def solicitarcoleta(self):
        rua = self.ids.rua_field.text
        numero = self.ids.numero_field.text
        complemento = self.ids.complemento_field.text
        cidade = self.ids.cidade_field.text
        cep = self.ids.cep_field.text
        item = self.ids.item_field.text

        data_hora_atual = datetime.now()

        db = firestore.client()

        endereco_ref = db.collection('Coletas_Solicitadas').document()

        dados_endereco = {
            'rua': rua,
            'numero': numero,
            'complemento': complemento,
            'cidade': cidade,
            'cep': cep,
            'item': item,
            'motorista': None,
            'data': self.data_selecionada.strftime('%d/%m/%Y') if self.data_selecionada else data_hora_atual.strftime('%d/%m/%Y'),
            'hora': self.hora_selecionada.strftime('%H:%M') if self.hora_selecionada else data_hora_atual.strftime('%H:%M')
        }

        endereco_ref.set(dados_endereco)

        self.ids.rua_field.text = ''
        self.ids.numero_field.text = ''
        self.ids.cidade_field.text = ''
        self.ids.bairro_field.text = ''
        self.ids.complemento_field.text = ''
        self.ids.cep_field.text = ''
        self.ids.item_field.text = ''

        self.show_confirmation_dialog()

    def show_confirmation_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Solicitação de coleta enviada com sucesso!",
                buttons=[
                    MDRaisedButton(
                        text="OK",
                        on_release=self.close_dialog
                    )
                ]
            )
        self.dialog.open()

    def close_dialog(self, instance):
        self.dialog.dismiss()

    def voltartelaprincipal(self):
        self.manager.current = 'tela_principal'

class BaixarEntregas(Screen):
    tipo_selecionado = ""
    regiao_selecionado = ""
    dialog = None

    def salvar_tipo(self, tipo):
        self.tipo_selecionado = tipo

    def salvar_regiao(self, regiao):
        self.regiao_selecionado = regiao

    def baixar_entrega(self):
        tipo = self.tipo_selecionado
        regiao = self.regiao_selecionado
        descricao = self.ids.descricao_field.text
        data_hora_atual = datetime.now()

        db = firestore.client()
        entrega_ref = db.collection('Baixar_Entregas').document()

        dados_entrega = {
            'tipo': tipo,
            'regiao': regiao,
            'descricao': descricao,
            'data_hora': data_hora_atual.strftime('%d/%m/%Y %H:%M')
        }

        entrega_ref.set(dados_entrega)

        self.ids.descricao_field.text = ''

        self.confirmacaoentrega_dialog()

    def confirmacaoentrega_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Entrega Confirmada!",
                buttons=[
                    MDRaisedButton(
                        text="OK",
                        on_relase=self.fecharconfirmacaoentrega
                    )
                ]
            )
        self.dialog.open()
    def fecharconfirmacaoentrega(self, instance):
        self.dialog.dismiss()

    def encerrar_lista(self):
        data_hora_atual = datetime.now()

        db = firestore.client()
        encerramento_ref = db.collection('Encerramento_Listas').document()

        dados_encerramento = {
            'data_hora_encerramento': data_hora_atual.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'encerrada'
        }

        encerramento_ref.set(dados_encerramento)
        print("Lista encerrada e registrada no banco de dados.")
        self.manager.current = 'tela_principal'

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.screen_manager = ScreenManager()
        self.load_kv_files()
        self.add_screens()
        return self.screen_manager

    def voltartelaprincipal(self):
        self.screen_manager.current = 'tela_principal'

    def voltar_ver_status(self):
        self.screen_manager.current = "ver_coletas"

    def load_kv_files(self):
        Builder.load_file("app.kv")  # Certifique-se de usar o nome correto do arquivo KV

    def segmented_control_selected(self, text):
        # Obtém a tela atualmente ativa
        current_screen = self.screen_manager.current_screen

        # Verifica se a tela atual é BaixarEntregas e se o atributo tipo_selecionado está presente na classe
        if isinstance(current_screen, BaixarEntregas) and hasattr(current_screen, "tipo_selecionado"):
            current_screen.tipo_selecionado = text

    def add_screens(self):
        self.screen_manager.add_widget(LoginScreen(name="login"))
        self.screen_manager.add_widget(TelaPrincipal(name="tela_principal"))
        self.screen_manager.add_widget(SolicitarColeta(name="solicitar_coleta"))
        self.screen_manager.add_widget(BaixarEntregas(name="baixar_entregas"))
        self.screen_manager.add_widget(VerStatus(name="ver_coletas"))
        self.screen_manager.add_widget(ColetasPedidas(name="coletas_pedidas"))
        self.screen_manager.add_widget(EntregasFeitas(name="entregas_feitas"))

if __name__ == "__main__":
    MainApp().run()
