from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from oppserver.models import GameData
import json
import time


class gameElements:
    pass

def get_movestring(game, instance):
    destination = 0
    newdest = True
    movestring = ''
    while len(movestring) < 60:
        if newdest:
            if game.ball_vx > 0:
                destination = 0
                destination = (((instance.board_width - game.ball_x) / (game.ball_vx * game.delta)) * (game.ball_vy * game.delta)) + game.ball_y
                shifted_dest = destination + (instance.board_height / 2)
                shifted_dest = shifted_dest % (2 * instance.board_height)
                if shifted_dest > instance.board_height:
                    shifted_dest = (2 * instance.board_height) - shifted_dest
                destination = shifted_dest - (instance.board_height / 2)
                if destination > ((instance.board_height / 2) - instance.hPadHeight):
                    destination = ((instance.board_height / 2) - instance.hPadHeight)
                elif destination < -((instance.board_height / 2) - instance.hPadHeight):
                    destination = -((instance.board_height / 2) - instance.hPadHeight)
            else:
                destination = 0
            print(destination)
            newdest = False
        else:
            if game.padR_y < destination - (instance.movement * game.delta):
                movestring += 'w'
                game.padR_y = game.padR_y + (instance.movement * game.delta)
            elif game.padR_y > destination + (instance.movement * game.delta):
                movestring += 's'
                game.padR_y = game.padR_y - (instance.movement * game.delta)
            else:
                movestring += 'x'
                break
    return movestring


@csrf_exempt
def calc_move( request ):
    if request.method != 'POST':
        return HttpResponse('', status=405)
    game = gameElements()
    instance = None
    try:
        instructions = json.loads(request.body)
        gameid = instructions['gameid']
        game.ball_x = instructions['ballX']
        game.ball_y = instructions['ballY']
        game.ball_vx = instructions['ballSpeedX']
        game.ball_vy = instructions['ballSpeedY']
        game.padR_y = instructions['paddlePos']
        game.delta = instructions['delta']
        instance = GameData.objects.get(id=gameid)
    except KeyError:
        return HttpResponse('', status=400)
    except GameData.DoesNotExist:
        return HttpResponse('', status=404)
    instance.last_update = time.time() * 1000
    instance.save()
    movestring = get_movestring(game, instance)
    return HttpResponse(movestring, status=200)


def tidy_up_db():
    try:
        dead_games = GameData.objects.filter(last_update__lte=((time.time() * 1000) - 60000))
        dead_games.delete()
    except:
        pass


@csrf_exempt
def manage_games( request ):
    instance = None
    if request.method != 'POST':
        return HttpResponse('', status=405)
    try:
        verb = ''
        data = json.loads(request.body)
        verb = data['verb']
        if verb == 'start':
            height = data['height']
            width = data['width']
            mode = data['mode']
            pheight = data['halfPadHeight']
            move = data['movement']
        elif verb == 'stop':
            gameid = data['id']
    except KeyError:
        return HttpResponse('', status=400)
    except:
        return HttpResponse('', status=500)

    tidy_up_db()
    if verb == 'start':
        try:
            instance = GameData.objects.create(board_height=height, board_width=width, game_mode=mode, hPadHeight=pheight, movement=move, last_update=int(time.time() * 1000))
        except:
            return HttpResponse('', status=500)
        print(instance.id)
        return HttpResponse(str(instance.id), status=200)
    elif verb == 'stop':
        try:
            instance = GameData.objects.get(id=gameid)
            instance.delete()
        except GameData.DoesNotExist:
            return HttpResponse('', status=404)
        except:
            return HttpResponse('', status=500)
        return HttpResponse('', status=204)
    else:
        return HttpResponse('', status=400)

