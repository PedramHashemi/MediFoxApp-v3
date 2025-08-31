from datetime import datetime
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from langgraph.checkpoint.memory import MemorySaver
import logging

from .models import Patient, ChatMessage
from .simpleAgent.doctor import stream_graph_updates, build_agent


logger = logging.getLogger(__name__)

config = {"configurable": {"thread_id": "1"}}
memory = MemorySaver()
agent = build_agent(checkpointer=memory)


class Home(View):
    def get(self, request):
        if request.user.is_authenticated:
            context = {
                "patient": request.user
            }
            return render(request=request, template_name="home.html", context=context)
        return redirect("main")

class Main(View):
    """Main and home page of Medifox."""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request=request, template_name='main.html')

class Login(View):
    """View for user login."""
    def get(self, request):
        return render(request=request, template_name='login.html')
    
    def post(self, request):
        data = request.POST.dict()

        user = authenticate(
            request=request,
            username = data.get("username"),
            password=data.get("password")
        )
        if user:
            login(request=request, user=user)
            return redirect("chat")


class Logout(View):
    """User Logout."""
    def get(self, request):
        logout(request)
        return redirect('main')

class Register(View):
    """This View allows the user to register."""
    def get(self, request):
        return render(request=request, template_name='register.html')
    
    def post(self, request):
        context = {}
        data = request.POST.dict()

        try:
            new_patient = User()

            new_patient.first_name = data.get("first_name")
            new_patient.last_name = data.get("last_name")
            new_patient.username = data.get("username")
            new_patient.email = data.get("email")
            new_patient.set_password(data.get("password"))

            new_patient.save()

            patient = authenticate(
                request=request,
                username=data.get("username"),
                password=data.get("password")
            )
            if patient:
                login(request=request, User=patient)
                return redirect("home")

        except Exception as e:
            context.update({"error": f"Unable to Register!! \n {e}"})

        return render(request=request, template_name="chat.html", context=context)



class Chat(View):
    """This View presents the chat environment with the medical agent."""
    def get(self, request):
        context = {
            "patient": request.user
        }
        return render(request=request, template_name='chat.html', context=context)

    def post(self, request):
        try:
            user_message = request.POST.get("message")
            logger.info("----------")
            logger.info(user_message)
            q_chat_message = ChatMessage(
                user=request.user,
                message=user_message,
                user_is_sender=True
            )
            q_chat_message.save()

            # medifox_message = stream_graph_updates(agent, user_message, config=config)
            medifox_message="How can I help you today? do you still have backpain?"
            chat_message = ChatMessage(
                user=request.user,
                # message=medifox_message,
                user_is_sender=False,
                parent_message_id=q_chat_message
            )
            chat_message.save()
            # print(chat_message.content)
            response_data = {
                'date': str(datetime.today().date()),
                'time': ':'.join([str(datetime.now().hour), str(datetime.now().minute)]),
                'medifox_message': medifox_message,
                'response': "Message received successfully!!"
            }
            return JsonResponse(response_data)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=400)
        


class ExtraDocs(View):
    """In This View the user adds extra documents."""
    def get(self, reuqest):
        return redirect("home")
