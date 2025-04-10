from res.character import Character
import res.character


# liora = Character("Liora", "Paladin", 15, 8, 15, 12, 12)
liora = res.character.from_file("liora_virelle")
print(liora.__repr__)
