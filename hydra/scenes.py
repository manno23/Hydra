__author__ = 'Jason'


class Scene(object):
    """
    Scene

    Each scene specified interprets the messages differently depending
    on how we want the client interface to interact with the midi playing.

    Within a scene messages may be targeted to all clients OR selected clients,
    and the clients targeted may change during the lifetime of the scene.

    The current state of the scene must be maintained here so that all clients
    are reflecting the same model despite their own state.
    """
    def __init__(self, scene_id):
        """
        Default constructor.
        @param scene_id: The ID for the scene that is agreed upon by the
                         clients in the policy.
        @param midi_input: Writes to the virtual midi instrument buffer.
        """
        self.id = scene_id

    def handle_midi(self, msg_type, channel, data1, data2, data3):
        """

        Converts the output midi from the application to the scene specific
        client messages.
        (ie. The scene directs midi to ask the ClientManager to select a
        client, then sends a message to the client to display the its state
        as active, then accept that clients messages and direct these to the
        midi.)

        @param msg_type: single midi message to be interpreted and converted
                         based on the scene policy
        @param channel:
        @param data1:
        @param data2:
        @param data3:
        @param timestamp:
        @return: packed string consisting of the message
                 to be used by the client.

         Also a target_profile, this details what clients to target, when to
         change the targets. The clientmanager manages who the selected clients
         are. If None targets all clients, otherwise each message in list is
         delivered to the selected clients.
        """
        pass

    def scene_state_message(self):
        """
        Compiles all the state of the object and prepares it as a
        message ready for communicating.
        @return: a byte array of the form
        byte[0]: scene id
        byte[1]: the state of the scene, details in the shared policy
        """
        pass

# Example Scenes
class NotActiveScene(Scene):
    def handle_midi(self, msg_type, channel, data1, data2, data3):
        return None

    def scene_state_message(self):
        return struct.pack('B', self.id)

class FountainScene(Scene):
    def __init__(self, scene_id):
        Scene.__init__(self, scene_id)

        # Fountain Scene state determined by incoming
        self.background_white = 1
        self.fountain_speed = 150

    def handle_midi(self, msg_type, channel, data1, data2, data3):
        """
        Kick = []
        Snare = [1]
        A single channel is assigned to every unique voicing

        @param msg_type:
        @param channel:
        @param data1:
        @param data2:
        @param data3:
        @param timestamp:
        @return: Type of message handler which can be of the type,
                     Message to send, with channel specifying the target
                     Update client information,
                        Make client active for channel/instrument, send message
                        Make channel/instrument inactive therefore remove those
                        clients, send message
                 The channel the midi was taken from to determine which clients
                 to send the message to
        """

        if msg_type is NOTE_ON and data1 is 36:
            # Messages for all clients
            self.background_white = not self.background_white
            if self.background_white:
                return struct.pack('BBB', SERVER_SCENE_UPDATE, 0, 0)
            else:
                return struct.pack('BBB', SERVER_SCENE_UPDATE, 0, 1)

        elif msg_type is PITCH_BEND:
            self.fountain_speed = data2
            return struct.pack('BBB', SERVER_SCENE_UPDATE, 1, data2)

        else:
            return None

    def scene_state_message(self):
        return struct.pack('BB',
                           self.background_white,
                           self.fountain_speed)

class ConcentricCircleScene(Scene):
    def __init__(self, scene_id):
        Scene.__init__(self, scene_id)
        self.MSG_HIT = 1

    def handle_midi(self, msg_type, channel, data1, data2, data3):
        if msg_type is NOTE_ON:
            if data1 is 40:
                return struct.pack('B', self.MSG_HIT)
        return None

    def scene_state_message(self):
        return struct.pack('B', self.id)

