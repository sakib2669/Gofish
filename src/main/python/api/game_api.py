from flask import request, jsonify
from flask_socketio import socketio, emit
from gamedb import NoSuchGameError
from app import app, game_repository
from errors import NotFoundError, ValidationError
from auth import authenticate

GAMES_PATH = "/games"


# Helper function similar to user_to_dict
def game_to_dict(game):
    """ Converts a Game object into a dictionary for JSON responses. """
    return {
        "game_id": game.gid,
        "creator": game.creator,
        "players": game.players,
        "creation_date": game.creation_date.isoformat(),
        "custom": game.custom,
        "href": f"{GAMES_PATH}/{game.gid}",
        "links": {
            "self": f"{GAMES_PATH}/{game.gid}",
            "update": f"{GAMES_PATH}/{game.gid}",
            "delete": f"{GAMES_PATH}/{game.gid}"
        }
    }


@socketio.on('draw_card')
@authenticate
def create_game():
    if not request.is_json:
        raise ValidationError("request body must be JSON")

    input_data = request.get_json()
    creator = input_data.get('creator')
    players = input_data.get('players')
    # Add other game creation related data as needed

    if not creator or not players:
        raise ValidationError("request must include creator and players")

    game = game_repository.create_game(creator=creator, players=players)

    output_data = game_to_dict(game)
    return jsonify(output_data), 201, {"Location": output_data['href']}


@socketio.on('ask_for_card')
def fetch_game(game_id: str):
    try:
        game = game_repository.find_game(game_id)
    except NoSuchGameError:
        raise NotFoundError(f"game {game_id} not found")
    return jsonify(game_to_dict(game)), 200


@app.route(f"{GAMES_PATH}/<game_id>", methods=["PUT"])
def update_game(game_id: str):
    if not request.is_json:
        raise ValidationError("request body must be JSON")

    input_data = request.get_json()
    try:
        existing_game = game_repository.find_game(game_id)
        updated_game = existing_game  # Assuming you have a way to update the game object
        # Update the game object with new data from input_data
        # For example: updated_game.players = input_data.get('players')

        game_repository.replace_game(updated_game)
        return jsonify(game_to_dict(updated_game)), 200
    except NoSuchGameError:
        raise NotFoundError(f"game {game_id} not found")


@app.route(f"{GAMES_PATH}/<game_id>", methods=["DELETE"])
def delete_game(game_id: str):
    try:
        game_repository.delete_game(game_id)
        return '', 204
    except NoSuchGameError:
        raise NotFoundError(f"game {game_id} not found")


@app.route(f"{GAMES_PATH}/<game_id>/draw", methods=['POST'])
def draw_card(game_id: str):
    data = request.json
    player_name = data.get('player_name')

    if not player_name:
        return jsonify({'error': 'Missing player_name'}), 400

    try:
        game = game_repository.find_game(game_id)
    except NoSuchGameError:
        return jsonify({'error': 'Game not found'}), 404

    player = next((p for p in game.players if p.name == player_name), None)
    if not player:
        return jsonify({'error': 'Player not found'}), 404

    card = player.draw(game.deck)
    if card:
        game_repository.update_game(game)  # Update the game state in the repository
        return jsonify({'message': f'{player_name} drew a card', 'card': str(card)}), 200
    else:
        return jsonify({'error': 'No more cards in the deck'}), 400


@app.route(f"{GAMES_PATH}/<game_id>/ask", methods=['POST'])
def ask_for_card(game_id: str):
    data = request.json
    asking_player_name = data.get('asking_player')
    target_player_name = data.get('target_player')
    rank = data.get('rank')

    if not asking_player_name or not target_player_name or not rank:
        return jsonify({'error': 'Missing required data'}), 400

    try:
        game = game_repository.find_game(game_id)
    except NoSuchGameError:
        return jsonify({'error': 'Game not found'}), 404

    if not game.is_current_player_turn(asking_player_name):
        return jsonify({'error': 'Not your turn'}), 403

    asking_player = next((p for p in game.players if p.name == asking_player_name), None)
    if not asking_player:
        return jsonify({'error': 'Asking player not found'}), 404

    message = game.ask_for_card(asking_player, target_player_name, rank)
    game_repository.update_game(game)  # Update the game state in the repository
    return jsonify({'result': message}), 200
