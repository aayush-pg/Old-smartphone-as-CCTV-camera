from flask_socketio import emit

def register_signaling_events(socketio):
    # 👇 THIS LINE PROVES THE CODE IS LOADED
    print("\n🔥🔥🔥 V3 SIGNALING LOGIC LOADED SUCCESSFULLY 🔥🔥🔥\n")

    # 1. Handle WebRTC "Offer"
    @socketio.on("offer")
    def on_offer(data):
        print(f"⚡ DEBUG: I received an OFFER! Data: {data}") # Debug print
        
        # Check for BOTH names to be safe
        room = data.get("room_code") or data.get("room")
        
        if room:
            print(f"✅ Forwarding OFFER to room: {room}")
            emit("offer", data, room=room, include_self=False)
        else:
            print("❌ ERROR: No Room ID in offer data!")

    # 2. Handle WebRTC "Answer"
    @socketio.on("answer")
    def on_answer(data):
        print(f"⚡ DEBUG: I received an ANSWER! Data: {data}")
        room = data.get("room_code") or data.get("room")
        if room:
            print(f"✅ Forwarding ANSWER to room: {room}")
            emit("answer", data, room=room, include_self=False)

    # 3. Handle ICE Candidates
    @socketio.on("ice-candidate")
    def on_ice_candidate(data):
        # We comment this out to keep logs clean, but it works same way
        room = data.get("room_code") or data.get("room")
        if room:
            emit("ice-candidate", data, room=room, include_self=False)