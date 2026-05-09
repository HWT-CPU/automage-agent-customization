import { create } from 'zustand'
import { workflowNodes, type WorkflowNode } from '../data/demoWorkflow'

interface WorkflowState {
  nodes: WorkflowNode[]
  selectedNode?: WorkflowNode
  setSelectedNode: (nodeId: string) => void
  setNodeStatus: (nodeId: string, status: WorkflowNode['status']) => void
  resetRun: () => void
}

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  nodes: workflowNodes,
  selectedNode: undefined,
  setSelectedNode: (nodeId) => {
    const node = get().nodes.find((item) => item.id === nodeId)
    set({ selectedNode: node })
  },
  setNodeStatus: (nodeId, status) =>
    set((state) => ({
      nodes: state.nodes.map((node) => (node.id === nodeId ? { ...node, status } : node)),
    })),
  resetRun: () => set({ nodes: workflowNodes, selectedNode: undefined }),
}))
