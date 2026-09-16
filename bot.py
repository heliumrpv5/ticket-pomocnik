import discord
from openai import OpenAI

# --- NASTAVITVE (Tukaj vpiši svoje podatke) ---
TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STAFF_ROLE_ID = int(os.getenv(1533932304135880804))  # Zamenkaj z ID-jem vaše staff vloge (številke)
# ---------------------------------------------

client_ai = OpenAI(api_key=OPENAI_API_KEY)
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"Uspešno prijavljen kot {bot.user}!")
    print("AI bot za tickete je pripravljen in deluje 24/7.")

@bot.event
async def on_message(message):
    # Ignoriraj sporočila, ki jih pošlje bot sam ali drugi boti
    if message.author.bot:
        return

    # Preverimo, ali se kanal začne s "ticket-" (prilagodi predpono, če jo tvoj Ticketer bot imenuje drugače)
    if message.channel.name.startswith("ticket-"):
        
        # Preverimo, ali je pošiljatelj član osebja
        is_staff = any(role.id == STAFF_ROLE_ID for role in message.author.roles)
        
        if is_staff:
            # Če je osebje nekaj napisalo, AI ne naredi ničesar in pusti prostor adminu
            return

        # Preverimo zgodovino kanala, da vidimo, ali se je osebje že oglasilo v tem tiketih
        staff_already_replied = False
        async for past_message in message.channel.history(limit=30):
            if not past_message.author.bot:
                past_is_staff = any(role.id == STAFF_ROLE_ID for role in past_message.author.roles)
                if past_is_staff:
                    staff_already_replied = True
                    break
        
        # Če se je osebje v tem tiketih že oglasilo, AI več ne odgovarja
        if staff_already_repeted := staff_already_replied:
            return

        # AI ustvari odgovor, ker osebje še ni poseglo v ta ticket
        try:
            response = client_ai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "Si prijazen in uradni pomočnik v podporni službi Helium RP serverja. Odgovarjaj točno, vljudno in profesionalno v slovenskem jeziku. Nikoli si ne izmišljaj lažnih podatkov, pravil ali IP-jev."
                    },
                    {"role": "user", "content": message.content}
                ],
                temperature=0.2 # Nizka temperatura, da preprečimo izmišljanje (halucinacije)
            )
            reply = response.choices[0].message.content
            await message.channel.send(f"🤖 **Ticket Pomočnik:** {reply}")
            
        except Exception as e:
            print(f"Napaka pri komunikaciji z OpenAI API: {e}")

bot.run(TOKEN)