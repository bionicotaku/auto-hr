"use client";

import { useMutation } from "@tanstack/react-query";

import { createJobFromDescription, createJobFromForm } from "@/lib/api/jobs";
import type {
  CreateJobDraftResponseDto,
  CreateJobFromDescriptionRequestDto,
  CreateJobFromFormRequestDto,
} from "@/lib/api/types";

export function useCreateJobFromDescriptionMutation() {
  return useMutation<CreateJobDraftResponseDto, Error, CreateJobFromDescriptionRequestDto>({
    mutationFn: createJobFromDescription,
  });
}

export function useCreateJobFromFormMutation() {
  return useMutation<CreateJobDraftResponseDto, Error, CreateJobFromFormRequestDto>({
    mutationFn: createJobFromForm,
  });
}

