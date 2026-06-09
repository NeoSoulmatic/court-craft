import axios from "axios"

import type { DraftPick, Game, Health, Player, Prediction, Team } from "@/types"

const api = axios.create({
  baseURL: "/api/v1",
  timeout: 15000,
})

export async function getHealth(): Promise<Health> {
  const { data } = await api.get<Health>("/health")
  return data
}

export async function getTeams(): Promise<Team[]> {
  const { data } = await api.get<Team[]>("/teams")
  return data
}

export async function getPlayers(params?: {
  team_id?: number
  active_only?: boolean
  search?: string
  limit?: number
}): Promise<Player[]> {
  const { data } = await api.get<Player[]>("/players", { params })
  return data
}

export async function getDraftSeasons(): Promise<string[]> {
  const { data } = await api.get<string[]>("/draft/seasons")
  return data
}

export async function getGames(params?: {
  season?: string
  limit?: number
}): Promise<Game[]> {
  const { data } = await api.get<Game[]>("/games", { params })
  return data
}

export async function getDraftPicks(params?: {
  season?: string
  limit?: number
}): Promise<DraftPick[]> {
  const { data } = await api.get<DraftPick[]>("/draft", { params })
  return data
}

export async function getUpcomingPredictions(): Promise<Prediction[]> {
  const { data } = await api.get<Prediction[]>("/predictions/upcoming")
  return data
}
