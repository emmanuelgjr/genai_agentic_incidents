# E16 title-similarity join — FOREMAN-GENERATED INPUT (2026-07-29)

Source cache: `ingest/_cache/aiaaic_sheet.csv` sha256 `fa2390ec67669f9b4cb0ac766ec5ce2d4545d8b433d9369701a777fb06dbd2ac` (961119 bytes)

Join: hand-curated `references[].url` last path segment -> sheet `summary` URL last path segment. Normalisation for comparison: lowercase, non-alphanumerics collapsed to single spaces, trimmed. Ratio = difflib.SequenceMatcher on the normalised strings.


## Band EXACT — 13 rows

| # | source_id | AIAAIC id | ratio | our `title` | AIAAIC `headline` |
|---|-----------|-----------|-------|-------------|-------------------|
| 1 | `AIAAIC-audio-deepfake-ceo` | AIAAIC0462 | 1.0 | Audio deepfake fraudulently impersonates CEO | Audio deepfake fraudulently impersonates CEO |
| 2 | `AIAAIC-bangladesh-news-anchor` | AIAAIC1422 | 1.0 | Deepfake news anchor accuses US of Bangladesh election interference | Deepfake news anchor accuses US of Bangladesh election interference |
| 3 | `AIAAIC-philippines-marcos` | AIAAIC1486 | 1.0 | Deepfake Philippines President urges military action against China | Deepfake Philippines President urges military action against China |
| 4 | `AIAAIC-taylor-swift-mandarin` | AIAAIC1164 | 1.0 | Taylor Swift speaks in Mandarin deepfake | Taylor Swift speaks in Mandarin deepfake |
| 5 | `AIAAIC-aoc-deepfake-porn` | AIAAIC1447 | 1.0 | Alexandria Ocasio-Cortez depicted as deepfake pornstar | Alexandria Ocasio-Cortez depicted as deepfake pornstar |
| 6 | `AIAAIC-opendream-csam` | AIAAIC1942 | 1.0 | OpenDream AI art generator accused of generating child sex images | OpenDream AI art generator accused of generating child sex images |
| 7 | `AIAAIC-gennomis-csam` | AIAAIC1941 | 1.0 | GenNomis AI art generator accused of producing explicit child images | GenNomis AI art generator accused of producing explicit child images |
| 8 | `AIAAIC-character-ai-suicide` | AIAAIC1781 | 1.0 | Boy commits suicide after relationship with Character.AI chatbot | Boy commits suicide after relationship with Character.AI chatbot |
| 9 | `AIAAIC-clearview-france` | AIAAIC1615 | 1.0 | French privacy watchdog fines Clearview AI for violating privacy | French privacy watchdog fines Clearview AI for violating privacy |
| 10 | `AIAAIC-duke-multi-tracking` | AIAAIC1536 | 1.0 | Duke University pulls facial-recognition dataset after privacy controversy | Duke University pulls facial recognition dataset after privacy controversy |
| 11 | `AIAAIC-outabox-biometric` | AIAAIC1705 | 1.0 | Outabox data breach exposes 1m biometric records | Outabox data breach exposes 1m biometric records |
| 12 | `AIAAIC-openai-deleted-datasets` | AIAAIC1485 | 1.0 | OpenAI deleted training datasets believed to contain copyrighted books | OpenAI deleted training datasets believed to contain copyrighted books |
| 13 | `AIAAIC-openai-stealing-pii` | AIAAIC1221 | 1.0 | OpenAI, Microsoft sued for 'stealing' personal info to create ChatGPT | OpenAI, Microsoft sued for 'stealing' personal info to create ChatGPT |

## Band >=0.8 — 47 rows

| # | source_id | AIAAIC id | ratio | our `title` | AIAAIC `headline` |
|---|-----------|-----------|-------|-------------|-------------------|
| 1 | `AIAAIC-proctoru-breach` | AIAAIC0470 | 0.98 | Data breach reveals data of 400,000+ ProctorU users | Data breach reveals data of 440,000 ProctorU users |
| 2 | `AIAAIC-singapore-sports-school` | AIAAIC1812 | 0.976 | Singapore Sports School students attacked with AI nude deepfakes | Singapore Sports School students attacked with nude deepfakes |
| 3 | `AIAAIC-south-korean-arrest-csam` | AIAAIC1186 | 0.972 | South Korean man arrested for using AI to create sexual images of children | South Korean arrested for using AI to create sexual images of children |
| 4 | `AIAAIC-megaface` | AIAAIC1555 | 0.972 | MegaFace facial-recognition dataset raises privacy and liability concerns | MegaFace facial recognition dataset raises privacy, liability concerns |
| 5 | `AIAAIC-apple-intelligence-scam-reword` | AIAAIC1873 | 0.963 | Apple Intelligence rewords and prioritises scam messages | Apple Intelligence rewords, prioritises scam messages |
| 6 | `AIAAIC-musk-harris-voiceclone` | AIAAIC1616 | 0.953 | Elon Musk shares Kamala Harris voice-clone video ad on X | Elon Musk shares Kamala Harris voice clone video ad |
| 7 | `AIAAIC-met-police-youth-worker` | AIAAIC1510 | 0.951 | Youth advocacy worker misidentified by Met Police facial recognition | Youth advocacy worker misidentified by Met Police facial recognition system |
| 8 | `AIAAIC-ai-impersonation-21k` | AIAAIC1006 | 0.945 | AI voice impersonation scams Canadian couple of USD 21,000 | AI impersonation scams Canadian couple of USD 21,000 |
| 9 | `AIAAIC-italian-sora-probe` | AIAAIC1415 | 0.939 | Italian privacy watchdog opens investigation into OpenAI Sora | Italian privacy watchdog opens investigation into Sora |
| 10 | `AIAAIC-french-police-fr` | AIAAIC1608 | 0.938 | French national police accused of illegally using facial recognition (Briefcam) | French national police accused of illegally using facial recognition |
| 11 | `AIAAIC-biden-draft-deepfake` | AIAAIC1163 | 0.935 | President Biden 'calls for US draft' deepfake video | President Biden calls for US draft deepfake |
| 12 | `AIAAIC-venezuela-news-anchors` | AIAAIC0972 | 0.925 | Deepfake news anchors claim Venezuela economic health | Deepfake news anchors extol Venezuela economic health |
| 13 | `AIAAIC-corsight-gaza` | AIAAIC1413 | 0.925 | Israeli Corsight facial-recognition system misidentifies innocent Gazans | Israel facial recognition system misidentifies innocent Gazans |
| 14 | `AIAAIC-eric-adams-robocalls` | AIAAIC1148 | 0.921 | NYC mayor Eric Adams robocalls residents using AI audio deepfakes | NYC mayor Eric Adams robocalls residents with audio deepfakes |
| 15 | `AIAAIC-cursor-fake-policy` | AIAAIC1956 | 0.909 | Cursor AI support agent invents user policy, causing user revolt | Cursor AI support agent invents user policy, causing uproar |
| 16 | `AIAAIC-chatgpt-leaky-code` | AIAAIC1158 | 0.902 | ChatGPT writes code that makes databases leak sensitive information | Study: ChatGPT writes code that makes databases leak sensitive info |
| 17 | `AIAAIC-brosnan-art-gallery` | AIAAIC1907 | 0.899 | Deepfake Pierce Brosnan scam cripples Nottingham art gallery | Deepfake Pierce Brosnan scam cripples art gallery |
| 18 | `AIAAIC-nudification-telegram` | AIAAIC1774 | 0.897 | AI nudification bots swamp Telegram | Studies: AI nudification bots swamp Telegram |
| 19 | `AIAAIC-software-engineers-suit` | AIAAIC1222 | 0.892 | Software engineers sue OpenAI, Microsoft for violating personal privacy (Copilot training) | Software engineers sue OpenAI, Microsoft for violating personal privacy |
| 20 | `AIAAIC-nomi-al-nowatzki` | AIAAIC1901 | 0.889 | Nomi AI chatbot recommends Al Nowatzki kills himself | Nomi AI chatbot recommends podcast host Al Nowatzki kills himself |
| 21 | `AIAAIC-clearview-ukraine` | AIAAIC0850 | 0.885 | Ukraine decision to use Clearview AI facial recognition draws concerns | Ukraine use of Clearview AI facial recognition draws concerns |
| 22 | `AIAAIC-mrbeast-iphone-scam` | AIAAIC1130 | 0.881 | Deepfake MrBeast iPhone giveaway scam on TikTok | Deepfake MrBeast iPhone giveaway scam |
| 23 | `AIAAIC-laion-5b-csam` | AIAAIC1249 | 0.881 | Child sexual abuse images discovered in LAION-5B training dataset | Child sex abuse images discovered on LAION-5B dataset |
| 24 | `AIAAIC-mary-nightingale-scam` | AIAAIC1660 | 0.879 | Mary Nightingale likeness used in AI-generated deepfake scam | Mary Nightingale likeness used in deepfake scam |
| 25 | `AIAAIC-telegram-deepfake-bot` | AIAAIC0347 | 0.873 | Telegram bot creates non-consensual deepfake porn at scale | Telegram AI bots create non-consensual deepfake porn |
| 26 | `AIAAIC-clearview-glasses` | AIAAIC0483 | 0.87 | Clearview AI tests live facial-recognition cameras and AR glasses | Clearview AI tests live facial recognition cameras |
| 27 | `AIAAIC-chatgpt-gdpr-correction` | AIAAIC1469 | 0.87 | ChatGPT said to violate GDPR by not correcting inaccurate personal info | ChatGPT accused of violating GDPR by not correcting inaccurate personal information |
| 28 | `AIAAIC-swinney-deepfake` | AIAAIC1474 | 0.865 | Deepfake John Swinney 'thanks Nicola Sturgeon' video | Deepfake John Swinney thanks Nicola Sturgeon for his election |
| 29 | `AIAAIC-civitai-csam` | AIAAIC1243 | 0.862 | CivitAI generates synthetic 'child pornography' images | CivitAI accused of generating synthetic 'child pornography' images |
| 30 | `AIAAIC-cadillac-fairview` | AIAAIC0148 | 0.861 | Cadillac Fairview covertly uses facial recognition to monitor shoppers | Cadillac Fairview discovered to be covertly using facial recognition to monitor shoppers |
| 31 | `AIAAIC-italy-bans-chatgpt` | AIAAIC1206 | 0.857 | Italy bans ChatGPT over GDPR privacy concerns (Garante) | Italy bans ChatGPT over data privacy concerns |
| 32 | `AIAAIC-nz-pensioner-224k` | AIAAIC1788 | 0.852 | New Zealand pensioner loses NZD 224,000 to deepfake Luxon Bitcoin scam | Pensioner loses NZD 224,000 to deepfake Bitcoin scam |
| 33 | `AIAAIC-nomi-violence` | AIAAIC1939 | 0.85 | Nomi AI companion bot incites self-harm, sexual violence, terror attacks | Nomi AI companion bot faces scrutiny for inciting self-harm, sexual violence, terror attacks |
| 34 | `AIAAIC-chatgpt-bug-history` | AIAAIC0985 | 0.842 | ChatGPT Redis bug exposes user chat histories and payment data | ChatGPT bug exposes user chat histories, payment info |
| 35 | `AIAAIC-chatgpt-leaks-user-convos` | AIAAIC1120 | 0.841 | ChatGPT leaks user conversations and personal information across sessions | ChatGPT leaks user conversations, personal information |
| 36 | `AIAAIC-cense-ai-leak` | AIAAIC0315 | 0.841 | Cense AI exposes 2.5 million personal records on open database | Cense AI exposes 2.5 million personal records |
| 37 | `AIAAIC-replika-italy-ban` | AIAAIC1178 | 0.839 | Replika hit with data-processing ban in Italy over child-safety concerns | Replika hit with data ban in Italy over child safety |
| 38 | `AIAAIC-chatgpt-walters-defamation` | AIAAIC1208 | 0.835 | ChatGPT falsely accuses Mark Walters of fraud and embezzlement (US defamation suit) | ChatGPT falsely accuses Mark Walters of fraud, embezzlement |
| 39 | `AIAAIC-taylor-swift-lecreuset` | AIAAIC1293 | 0.831 | Deepfake Taylor Swift fake Le Creuset cookware giveaway scam | Deepfake Taylor Swift offers free Le Creuset cookware scam |
| 40 | `AIAAIC-chatgpt-opencage` | AIAAIC0958 | 0.828 | ChatGPT falsely tells users OpenCage offers reverse-phone-lookup service | ChatGPT falsely accuses OpenCage of 'phone lookup' service |
| 41 | `AIAAIC-energy-243k-voice-clone` | AIAAIC0227 | 0.825 | Fraudsters clone CEO voice to steal USD 243,000 from UK energy firm | Fraudsters clone CEO voice to steal USD 243,000 |
| 42 | `AIAAIC-civitai-deepfakes` | AIAAIC1190 | 0.816 | CivitAI rewards deepfakes of real people via 'bounty' system | CivitAI rewards deepfakes of real people |
| 43 | `AIAAIC-clearview-ai` | AIAAIC0320 | 0.816 | Clearview AI mass facial-recognition scraping | Clearview AI facial recognition |
| 44 | `AIAAIC-thomson-fraud-detect` | AIAAIC1288 | 0.814 | Thomson Reuters Fraud Detect 'incorrectly' identifies fraud against welfare claimants | Thomson Reuters Fraud Detect 'incorrectly' identifies fraud |
| 45 | `AIAAIC-remini-csam` | AIAAIC1100 | 0.811 | Remini AI photo enhancer generates 'child porn' from innocent photos | Remini AI photo enhancer generates 'child porn' |
| 46 | `AIAAIC-slovakia-audio` | AIAAIC1137 | 0.805 | Deepfake audio claims Slovakian opposition leaders tried to rig election | Deepfake audio recording claims opposition leaders tried to rig Slovakian election |
| 47 | `AIAAIC-chatgpt-psychosis` | AIAAIC2110 | 0.804 | ChatGPT drives Jacob Irwin into psychosis ('AI-induced delusion') | ChatGPT drives Jacob Irwin into psychosis |

## Band 0.6-0.8 — 19 rows

| # | source_id | AIAAIC id | ratio | our `title` | AIAAIC `headline` |
|---|-----------|-----------|-------|-------------|-------------------|
| 1 | `AIAAIC-muah-companion-hack` | AIAAIC1764 | 0.797 | Muah AI companion app hack reveals attempts to simulate child abuse | AI companion app Muah hack reveals users trying to simulate child abuse |
| 2 | `AIAAIC-maxpread-fake-ai-ceo` | AIAAIC1077 | 0.796 | Maxpread Technologies fabricated AI CEO scam | Maxpread Technologies fake AI CEO investment scam |
| 3 | `AIAAIC-xtwitter-swift-images` | AIAAIC1314 | 0.791 | X/Twitter fails to remove non-consensual AI deepfake images of Taylor Swift | X/Twitter fails to remove graphic AI images of Taylor Swift |
| 4 | `AIAAIC-korean-schools-deepfake` | AIAAIC1727 | 0.791 | Deepfake porn engulfs Korean schools ('New Nth Room') | Deepfake porn engulfs South Korean schools |
| 5 | `AIAAIC-air-canada-liable` | AIAAIC1339 | 0.783 | Air Canada found liable for chatbot's incorrect bereavement-fare advice | Air Canada found liable for chatbot's poor advice |
| 6 | `AIAAIC-these-nudes` | AIAAIC0345 | 0.781 | These Nudes Do Not Exist commercial deepfake porn marketplace | These Nudes Do Not Exist deepfake porn sales |
| 7 | `AIAAIC-wpp-ceo-deepfake` | AIAAIC1483 | 0.755 | WPP CEO Mark Read impersonated in deepfake voice-cloning scam | WPP CEO impersonated in deepfake scam |
| 8 | `AIAAIC-faception` | AIAAIC050 | 0.752 | Faception 'facial personality profiling' pseudo-science marketing | Faception facial personality profiling |
| 9 | `AIAAIC-atlantic-plaza` | AIAAIC0267 | 0.738 | Atlantic Plaza Towers facial-recognition rollout opposed by tenants | Atlantic Plaza Towers facial recognition plan blasted as privacy intrusion |
| 10 | `AIAAIC-qtcinderella-deepfakes` | AIAAIC0960 | 0.736 | QTCinderella, Pokimane, Sweet Anita streamer deepfake porn | QTCinderella, Pokimane, Sweet Anita deepfakes exposed using live stream |
| 11 | `AIAAIC-drake-weeknd` | AIAAIC0992 | 0.703 | Drake / The Weeknd AI voice-cloning 'Heart on My Sleeve' | Drake, The Weeknd voices cloned using AI |
| 12 | `AIAAIC-chatgpt-bombs` | AIAAIC1738 | 0.694 | ChatGPT details how to make homemade bombs after safety bypass | Hacker discovers ChatGPT details how to make homemade bombs |
| 13 | `AIAAIC-canada-chatgpt-investigation` | AIAAIC1209 | 0.694 | Canada investigates ChatGPT privacy concerns | Canada launches investigation into ChatGPT over Privacy/surveillance concerns |
| 14 | `AIAAIC-automators-llc` | AIAAIC1289 | 0.689 | Automators AI online-sales coaching FTC fraud case | FTC sues Automators for misleading "AI" online sales and coaching fraud |
| 15 | `AIAAIC-putin-martial-law` | AIAAIC1033 | 0.68 | Putin 'declares martial law' deepfake broadcast hijack | Vladimir Putin declares Russia martial law deepfake |
| 16 | `AIAAIC-martin-lewis-scam-ad` | AIAAIC1056 | 0.674 | Martin Lewis deepfake scam ad on Facebook | Martin Lewis impersonated in deepfake scam ad |
| 17 | `AIAAIC-driver-chatbot-usd1` | AIAAIC1287 | 0.671 | Driver tricks dealership chatbot into selling Chevrolet for USD 1 (Watsonville-style incident) | Driver tricks dealership AI negotiation agent into selling car for USD 1 |
| 18 | `AIAAIC-wisconsin-thousands-children` | AIAAIC1917 | 0.654 | Wisconsin man arrested for AI-generating images of thousands of children | Wisconsin man arrested for using AI to create thousands of prepubescent minor images |
| 19 | `AIAAIC-gatlin-wrongful-arrest` | AIAAIC1872 | 0.615 | Christopher Gatlin facial-recognition wrongful arrest | Christopher Gatlin jailed for two years after faulty facial recognition match |

## Band <0.6 — 13 rows

| # | source_id | AIAAIC id | ratio | our `title` | AIAAIC `headline` |
|---|-----------|-----------|-------|-------------|-------------------|
| 1 | `AIAAIC-deepnude-app` | AIAAIC0210 | 0.581 | DeepNude nudification app | DeepNude nudification app provokes ethics, privacy controversy |
| 2 | `AIAAIC-everalbum` | AIAAIC0843 | 0.517 | Everalbum trains facial recognition on user photos and sells to law enforcement | Everalbum covertly uses personal data to train facial recognition system |
| 3 | `AIAAIC-south-korea-election-deepfakes` | AIAAIC0839 | 0.492 | South Korea presidential election candidate AI deepfakes | Yoon Suk-yeol presidential deepfake candidacy prompts concerns |
| 4 | `AIAAIC-xiao-yu-porn` | AIAAIC0771 | 0.481 | Xiao Yu deepfake pornography case | Taiwanese arrested, jailed for creating and selling deepfake pornography |
| 5 | `AIAAIC-yang-mi-athena` | AIAAIC0236 | 0.458 | Yang Mi and Athena Chu face-swap deepfake video | Athena Chu deepfake face swap prompts controversy |
| 6 | `AIAAIC-chatgpt-collect-pii` | AIAAIC1225 | 0.442 | ChatGPT used to collect users' personal information | Study: ChatGPT can be used to identify individual internet users |
| 7 | `AIAAIC-ince-porn-deepfake` | AIAAIC1014 | 0.432 | Muharrem Ince porn 'deepfake' withdrawal from Turkish election | Muharrem Ince withdraws from Türkiye election after porn 'deepfake' |
| 8 | `AIAAIC-biden-police-interview` | AIAAIC0389 | 0.43 | Joe Biden police-defunding deepfake interview | Deepfake Joe Biden threatens to defund US police |
| 9 | `AIAAIC-rcmp-clearview` | AIAAIC0645 | 0.423 | RCMP AI facial recognition surveillance ruled unlawful | RCMP violated Canadians' privacy using Clearview AI facial recognition |
| 10 | `AIAAIC-dubai-35m-voice-clone` | AIAAIC0775 | 0.336 | Dubai $35M voice-cloning fraud against UAE bank | Scammers use cloned voice to steal USD 35m from Dubai company |
| 11 | `AIAAIC-grok-chatbot` | AIAAIC1619 | 0.333 | Grok chatbot inaccuracies, hallucinations and harmful outputs | Grok chatbot |
| 12 | `AIAAIC-ftx-ceo-deepfake` | AIAAIC0893 | 0.321 | FTX CEO Sam Bankman-Fried deepfake crypto-recovery scam | Deepfake impersonating FTX CEO attempts to scam investors |
| 13 | `AIAAIC-arup-25m-cfo` | AIAAIC1321 | 0.304 | Arup Hong Kong $25M deepfake CFO multi-person video call scam | Deepfake CFO scams finance worker for USD 25 million |

## Band UNJOINED — 3 rows

| # | source_id | AIAAIC id | ratio | our `title` | AIAAIC `headline` |
|---|-----------|-----------|-------|-------------|-------------------|
| 1 | `AIAAIC-miami-pinecrest` | — | — | Miami Pinecrest Cove boys arrested for AI nude images of classmates | — |
| 2 | `AIAAIC-c4-dataset` | — | — | C4 dataset includes sites trafficking in pirated, hateful and surveillance content | — |
| 3 | `AIAAIC-books3-dataset` | — | — | Books3 dataset of pirated books used to train Llama and Bloom | — |
