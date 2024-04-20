import pprint
# from voice import Voice
# from modules import Voice
from modules.voice import Voice

def generate_voices(num_voices = 3, num_rows = 3) -> "list[Voice]":
    staff_map = {0:{}, 1:{}, 2:{}}
    top_staff = [ [[150, 110], [500, 110]], [[100, 370], [500, 370]], [[100, 630], [500, 630]] ]

    voices = [Voice(v, num_rows) for v in range(1,num_voices+1)]

    for staff_num, staff in enumerate(top_staff):
        # get staff
        start_staff = staff[0]
        end_staff = staff[1]

        # load staff
        staff_count = 0
        while staff_count < 15:
            # alter staff
            if staff_count != 0:
                start_staff[1] += 20 if staff_count % 5 == 0 else 15
                end_staff[1] += 20 if staff_count % 5 == 0 else 15

            print(f"adding voice {staff_count//5} {start_staff} {end_staff}")

            voices[staff_count // 5].add_staff(staff_num, start_staff.copy(), end_staff.copy())

            staff_count += 1

    return voices

def map_note(voices: "list[Voice]", x: int, y: int) -> tuple:
    found = False
    found_row = -1

    # look at the voices
    for voice in voices:
        # get staff range to find which voice
        staff_ranges = voice.get_staff_ranges()

        # check each range
        for row, staff_range in enumerate(staff_ranges):
            upper_staff, lower_staff = staff_range

            # evaluate if the note is within error
            if y >= upper_staff[0][1]-3 and y <= lower_staff[1][1]+3:
                found = True
                found_row = row
                break
        
        # find which staff in the voice if found
        if found:
            # gets the staff
            found_staff, staff_y_coordinate = voice.get_staff(found_row, y)

            if found_staff is None: break

            # add note to the voice
            voice.add_note(found_row, found_staff, x)

            # returns
            return (voice.voice, found_staff, staff_y_coordinate)
        
    return (None, None, None)

        