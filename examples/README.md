# PTP Examples

This directory shows inference examples on the PTP model, categorized by the features described in the thesis.

## Bad Normalization
This directory contains examples of inference on the model that was trained on the text normalization used for speech, showing major inaccuracies to the ground audio.

## Objective
Examples here showcase the model's ability to keep an accurate tempo throughout the sequence, and play the right pitches.

## Expressiveness
These clips demonstrate that the model is able to add expressive features to a sequence, such as variation in dynamics and tempo and the occasional unprompted arpeggio.

## Direct Audio
Samples in this directory have been directly generated from the ground truth audio using the WaveGlow model. This shows the existence of echoing noise is apparent even in this clips, and thus not a cause of the acoustic model.