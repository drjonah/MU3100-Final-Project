
class Voice:
    def __init__(self, voice: int, rows: int) -> None:
        self.voice = voice
        self.rows = rows
        self.staffs = [[] for _ in range(rows)]
        self.notes = [[] for _ in range(rows)]

    def add_staff(self, row: int, start: "list[int]", end: "list[int]") -> None:
        assert row < self.rows

        # add to staff
        self.staffs[row].append([tuple(start), tuple(end)])

    def get_staff_ranges(self) -> list[int]:
        ranges = []

        for row in range(self.rows):
            staff_group = self.staffs[row]
            ranges.append([staff_group[0], staff_group[-1]])

        return ranges

    def get_staff(self, row: int, y: int) -> tuple:
        staff_range = self.staffs[row]
        print(staff_range)
        
        for staff_num, staff in enumerate(staff_range):
            # not last staff because the last staff doesnt have a half step
            if (staff_num != 4) and (y > staff[0][1]+3 and y < staff_range[staff_num+1][0][1]-3):
                return ((staff_num * 2 + 2), staff[0][1]+7.5)
            
            # whole step evaluation
            if y >= staff[0][1]-3 and y <= staff[0][1]+3:
                return ((staff_num * 2 + 1), staff[0][1])
            
        return (None, None)
            
    def add_note(self, row: int, staff: int, x: int) -> None:
        # add note
        self.notes[row].append((staff, x))
        # sort by x
        self.notes[row].sort(key=lambda x: x[1])
        
        print(self.voice, self.notes)

