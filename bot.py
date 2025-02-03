import os
import discord
import uuid
import time
import requests
import asyncio
from tkinter import Tk, Label
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Your Discord bot token
TOKEN = os.getenv("DISCORD_TOKEN")

# Define the channel and user IDs
TARGET_CHANNEL_ID = 831029897479585832  # Replace with your channel ID
TARGET_USER_ID = 270904126974590976  # Replace with your user ID

# Folder to save images
if not os.path.exists('images'):
    os.makedirs('images')

# Set up intents for reading messages
intents = discord.Intents.default()
intents.message_content = True  # Allow the bot to read message content
intents.messages = True  # Allow the bot to read message history
intents.guilds = True  # Allow the bot to access guild information
intents.members = False  # Optional, for member-related events (not needed here)

# Create a client instance with intents
client = discord.Client(intents=intents)

# Generate a unique filename for each image
def generate_unique_filename():
    return f"{uuid.uuid4().hex}_{int(time.time())}"

# Check if the attachment is an image
def is_image(attachment):
    return attachment.content_type and attachment.content_type.startswith('image/')

# Check if the embed has an image
def is_embed_image(embed):
    return embed.image and embed.image.url

# Function to download the image
def download_image(url, filename):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Image saved as {filename}")
        else:
            print(f"Failed to download {url}, status code {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

# Delay between image downloads to avoid hitting rate limits
async def delay():
    await asyncio.sleep(0.5)

# Function to update message count in the GUI
def update_message_count(count):
    message_label.config(text=f"Messages processed: {count}")
    root.update_idletasks()

# Function that runs when the bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')  # Confirm login

    # Get the target channel by its ID
    channel = client.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        print("Failed to find channel.")
        return  # If channel is not found, exit the function
    
    print(f"Found channel: {channel.name}")  # Confirm that the channel was found
    
    # Initialize message count
    message_count = 0

    # Fetch messages from the specified channel (limit set to 100 to avoid hitting rate limits)
    async for message in channel.history(limit=35000):  # You can adjust the limit here
        if message.author.id != TARGET_USER_ID:  # Skip messages from other users
            continue
        
        print(f"Processing message from {message.author}")  # Print the message author being processed

        # Check if there are attachments and if the attachment is an image
        for attachment in message.attachments:
            if is_image(attachment):
                image_url = attachment.url
                unique_filename = generate_unique_filename() + os.path.splitext(attachment.filename)[1]
                image_name = os.path.join("images", unique_filename)
                print(f"Downloading image: {image_url}")
                
                # Download the image and save it
                download_image(image_url, image_name)
                
                # Wait for a bit before the next request
                await delay()

        # Check if the message has embeds (like Dank Memer bot images)
        for embed in message.embeds:
            if is_embed_image(embed):
                image_url = embed.image.url  # Get the image URL from the embed
                unique_filename = generate_unique_filename() + os.path.splitext(image_url.split('/')[-1])[1]
                image_name = os.path.join("images", unique_filename)
                print(f"Downloading embed image: {image_url}")
                
                # Download the image and save it
                download_image(image_url, image_name)
                
                # Wait for a bit before the next request
                await delay()

        # Update the message count in the GUI window
        message_count += 1
        update_message_count(message_count)

    # After processing, show a message in the GUI
    message_label.config(text="Finished processing all messages!")
    root.update_idletasks()

    # Close the window after a delay
    root.after(3000, root.quit)

# Set up the GUI window
root = Tk()
root.title("Discord Bot Image Downloader")
root.geometry("400x200")

message_label = Label(root, text="Messages processed: 0")
message_label.pack(pady=20)

# Start the bot
client.run(TOKEN)  # Replace with your bot token
