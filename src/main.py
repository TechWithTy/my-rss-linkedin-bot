from src.config_loader import config
from src.linkedin_bot import get_linkedin_profile_id, post_to_linkedin
from src.models.openai_generator import (
    create_openai_thread,
    send_message_to_openai,
    run_openai_assistant,
    wait_for_openai_response,
    get_openai_response
)
from src.medium_bot import fetch_latest_medium_blog
from src.utils.index import parse_html_blog_content
from src.utils.giphy import giphy_find_with_metadata, extract_social_upload_metadata


def fetch_and_parse_blog(username: str) -> str | None:
    blog_content = fetch_latest_medium_blog(username)
    if not blog_content:
        print("ℹ️ No blog content found.")
        return None
    return parse_html_blog_content(blog_content)


def run_openai_pipeline(blog_content: str) -> str | None:
    thread_id = create_openai_thread()
    if not thread_id:
        print("❌ Failed to create OpenAI thread.")
        return None

    send_message_to_openai(thread_id, blog_content)
    run_id = run_openai_assistant(thread_id)
    if not run_id:
        print("❌ Failed to run OpenAI assistant.")
        return None

    wait_for_openai_response(thread_id, run_id)
    return get_openai_response(thread_id)


def main(medium_username: str) -> None:
    try:
        linkedin_enabled = config['social_media_to_post_to']['linkedin'].get('enabled', False)
        print(f"🔄 LinkedIn Enabled: {linkedin_enabled} | Medium: {medium_username}")

        profile_id = get_linkedin_profile_id()
        if not profile_id:
            raise ValueError("Could not retrieve LinkedIn profile ID.")
        print("✅ LinkedIn authenticated.")

        parsed_blog = fetch_and_parse_blog(medium_username)
        if not parsed_blog:
            return

        # 🔁 REPLACE THIS STATIC OBJECT WITH OPENAI-DRIVEN GENERATION LATER
        linkedin_post = {
            "Text": "Tired of messy culturing workflows? We built a tool at Cyberoni that simplifies everything—from data management to label printing. Perfect for beginners & pros. No more chaos, just clarity. ✨ #CyberOniCommunity",
            "Hashtags": ["#AI", "#MachineLearning", "#DataScience", "#Automation", "#Technology"],
            "GifSearchTags": ["lab organization", "printing labels", "tech innovation"]
        }

        if linkedin_enabled:
            print("🚀 Preparing LinkedIn post...")

            gif_tags = linkedin_post.get("GifSearchTags", [])
            print(f"🔍 GIF search tags: {gif_tags}")

            if gif_tags:
                gif_result = giphy_find_with_metadata(gif_tags)
                print(gif_result,"gif_results")
                gif_obj = gif_result.get("result", {}).get("gif")
                print(gif_obj,"gif_obj")

                if gif_obj:
                    print("🎞️ Found GIF result, extracting metadata...")
                    linkedin_post["GifAsset"] = extract_social_upload_metadata(gif_obj)
                else:
                    print("❌ No GIF found from Giphy.")

            image_url = linkedin_post.get("ImageAsset")
            gif_asset = linkedin_post.get("GifAsset")

            print(f"🖼️ Image URL: {image_url}")
            print(f"🎬 GIF Asset: {gif_asset}")

            # Prepare final post content
            post_text = linkedin_post.get("Text", "")
            hashtags = linkedin_post.get("Hashtags", [])
            full_text = f"{post_text}\n{' '.join(hashtags)}" if hashtags else post_text

            print("📝 Final post text:")
            print(full_text)

            # Decide media type
            media_url = None
            media_type = None
            if gif_asset:
                media_url = gif_asset.get("mp4_url")
                media_type = "GIF"
                print(f"📦 Using GIF for post: {media_url}")
            elif image_url:
                media_url = image_url
                media_type = "IMAGE"
                print(f"🖼️ Using image for post: {media_url}")
            else:
                print("⚠️ No media asset found for the post.")

            # Post to LinkedIn
            if media_url and media_type:
                post_to_linkedin(
                    post_text=full_text,
                    profile_id=profile_id,
                    media_url=media_url,
                    media_type=media_type
                )
                print("✅ Successfully posted to LinkedIn!")
            else:
                print("🚫 Skipping post — no valid media asset was available.")

        else:
            print("🔕 LinkedIn post generation complete (posting disabled).")
            print(f"\n📋 Suggested Post:\n{linkedin_post}")

    except Exception as e:
        print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    medium_username = config['user_profile'].get('medium_username')
    if medium_username:
        main(medium_username)
    else:
        print("⚠️ Medium username not found in config.")
