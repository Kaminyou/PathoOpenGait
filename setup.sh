wget -O pretrained_h36m_detectron_coco.bin https://www.dropbox.com/scl/fi/qflj7utmg6klaq6tuxmpb/pretrained_h36m_detectron_coco.bin?rlkey=nmwv4lc1bq8986gngpej38usq
EXPECTED_HASH="d3219e005b50591f694da5cbaf6849f060d6b2cf895864a779f8a992ac63a232"

CALCULATED_HASH=$(sha256sum pretrained_h36m_detectron_coco.bin | awk '{ print $1 }')
# Compare the calculated hash to the expected hash
if [ "$CALCULATED_HASH" != "$EXPECTED_HASH" ]; then
  echo "Error: SHA-256 hash does not match"
else
  echo "SHA-256 hash matches"
  cp pretrained_h36m_detectron_coco.bin backend/algorithms/gait_basic/VideoPose3D/checkpoint/pretrained_h36m_detectron_coco.bin
fi

rm pretrained_h36m_detectron_coco.bin

wget -O epoch_94.pth https://www.dropbox.com/scl/fi/di8az1o4hgmv85uyg2hw0/epoch_94.pth?rlkey=6yxbjauub469ih2xcd82gkqia

EXPECTED_HASH="3878229e15542573a75948999ffff4d75d7dba3d00dbbe358bb2e15270348f08"

# Calculate the SHA-256 hash of the file
CALCULATED_HASH=$(sha256sum epoch_94.pth | awk '{ print $1 }')

# Compare the calculated hash to the expected hash
if [ "$CALCULATED_HASH" != "$EXPECTED_HASH" ]; then
  echo "Error: SHA-256 hash does not match"
else
  echo "SHA-256 hash matches"
  cp epoch_94.pth backend/algorithms/gait_basic/gait_study_semi_turn_time/weights/semi_vanilla_v2/epoch_94.pth
fi

rm epoch_94.pth

